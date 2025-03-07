from compeng_gg.auth import get_uid
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from quercus_app.models import QuercusUser
from quercus_app.rest_api import QuercusRestAPI

from courses.models import *
from discord_app.utils import *
from github_app.utils import *

def remove_enrollment(enrollment):
    user = enrollment.user
    print(f'    Removing {user.username}')

    # Remove Discord role and GitHub team membership
    safe_remove_discord_role_for_enrollment(enrollment)
    safe_remove_github_team_membership_for_enrollment(enrollment)

    try:
        remove_github_fork(enrollment)
    except:
        print('      GitHub Repository not found')

    offering = enrollment.role.offering
    for assignment in offering.assignment_set.all():
        AssignmentTask.objects.filter(user=user, assignment=assignment).delete()
        AssignmentLeaderboardEntry.objects.filter(user=user, assignment=assignment).delete()
        AssignmentGrade.objects.filter(user=user, assignment=assignment).delete()
        Accommodation.objects.filter(user=user, assignment=assignment).delete()
    enrollment.delete()

def change_role_from_student_to_audit(enrollment):
    user = enrollment.user
    role = enrollment.role

    # If they're already an audit, skip
    if role.kind == Role.Kind.AUDIT:
        return

    # Remove the student roles
    safe_remove_discord_role_for_enrollment(enrollment)
    safe_remove_github_team_membership_for_enrollment(enrollment)

    audit_role = Role.objects.get(offering=role.offering, kind=Role.Kind.AUDIT)
    enrollment.role = audit_role
    enrollment.save()

    safe_add_discord_role_for_enrollment(enrollment)
    safe_add_github_team_membership_for_enrollment(enrollment)

def _update(offering, quercus_users, role_kind):
    utoronto = Institution.objects.get(slug='utoronto')

    print(f'Updating {offering} {role_kind.label}s')
    role = offering.role_set.get(kind=role_kind)
    current_enrollments = Enrollment.objects.filter(role=role)
    print(f'  Current enrollments: {current_enrollments.count()}')
    users_removed = set([e.user for e in current_enrollments])

    print(f'  Quercus users: {len(quercus_users)}')
    for quercus_user in quercus_users:
        username = quercus_user['sis_user_id']
        # Likely the test student
        if username is None:
            continue
        quercus_user_id = quercus_user['id']
        # Skip non students
        if quercus_user['integration_id'] is None:
            continue
        student_id = int(quercus_user['integration_id'])
        user, _ = User.objects.get_or_create(username=username)
        try:
            member = user.member_set.get(institution=utoronto)
            assert member.external_id == student_id
        except Member.DoesNotExist:
            Member.objects.create(
                institution=utoronto, user=user, external_id=student_id
            )
        try:
            quercus_user = user.quercus_user
            assert quercus_user.id == quercus_user_id
        except QuercusUser.DoesNotExist:
            QuercusUser.objects.create(user=user, id=quercus_user_id)

        if user in users_removed:
            users_removed.remove(user)

        enrollment, enrollment_created = Enrollment.objects.get_or_create(
            user=user, role=role
        )
        if not enrollment_created:
            continue

        print('    Adding', user.username)

        # If they're already in Discord, give them the roles
        safe_add_discord_role_for_enrollment(enrollment)
        safe_add_github_team_membership_for_enrollment(enrollment)

        # If they're already connected to GitHub, create their repository
        try:
            get_uid('github', user)
            create_fork_for_enrollment(enrollment)
        except ObjectDoesNotExist:
            pass

    print(f"  Removed students: {len(users_removed)}")
    for user in users_removed:
        enrollment = Enrollment.objects.get(user=user, role=role)
        # This was remove_enrollment
        change_role_from_student_to_audit(enrollment)

def _get_instructor_with_token(offering):
    instructor = None
    instructor_role = offering.role_set.get(kind=Role.Kind.INSTRUCTOR)
    for enrollment in instructor_role.enrollment_set.all():
        try:
            enrollment.user.quercus_token
            instructor = enrollment.user
            break
        except User.quercus_token.RelatedObjectDoesNotExist:
            pass
    assert instructor is not None
    return instructor

def sync_assignment_to_quercus(assignment):
    offering = assignment.offering
    instructor = _get_instructor_with_token(offering)

    api = QuercusRestAPI(instructor)
    quercus_course_id = offering.external_id
    assert not quercus_course_id is None

    if assignment.external_id is None:
        quercus_assignment = api.create_assignment(
            quercus_course_id,
            f"{assignment.name} Autograder",
            assignment.overall_total
        )
        assignment.external_id = quercus_assignment["id"]
        assignment.save()

    data = {"grade_data": {}}
    student_role = offering.role_set.get(kind=Role.Kind.STUDENT)
    for enrollment in Enrollment.objects.filter(role=student_role):
        user = enrollment.user
        quercus_user = user.quercus_user
        quercus_user_id = quercus_user.id
        grade = 0.0
        try:
            assignment_result = AssignmentResult.objects.get(user=user, assignment=assignment)
            grade = assignment_result.overall_grade
        except AssignmentResult.DoesNotExist:
            pass
        data["grade_data"][str(quercus_user_id)] = {}
        data["grade_data"][str(quercus_user_id)]["posted_grade"] = grade
    api.update_grades(quercus_course_id, assignment.external_id, data)

def update_courses_from_quercus():
    for offering in Offering.objects.all():
        if offering.external_id is None:
            continue
        if not offering.active:
            continue
        instructor = _get_instructor_with_token(offering)
        api = QuercusRestAPI(instructor)
        quercus_course_id = offering.external_id
        students = api.list_students(quercus_course_id)
        _update(offering, students, Role.Kind.STUDENT)
        tas = api.list_tas(quercus_course_id)
        _update(offering, tas, Role.Kind.TA)
