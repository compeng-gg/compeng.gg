from compeng_gg.auth import get_uid
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from quercus_app.models import QuercusUser
from quercus_app.rest_api import QuercusRestAPI

from courses.models import *
from discord_app.utils import *
from github_app.utils import *

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
        try:
            get_uid('discord', user)
            try:
                add_discord_role_for_enrollment(enrollment)
            except:
                # Likely they left the server, handle this later
                pass
        except ObjectDoesNotExist:
            pass

        # If they're already connected to GitHub, add them
        try:
            get_uid('github', user)
            add_github_team_membership_for_enrollment(enrollment)
            create_fork_for_enrollment(enrollment)
        except ObjectDoesNotExist:
            pass

    print(f"  Removed students: {len(users_removed)}")
    for user in users_removed:
        enrollment = Enrollment.objects.get(user=user, role=role)
        print(f'    Removing {user.username}')
        # If they're already in Discord, remove the roles
        try:
            get_uid('discord', user)
            try:
                remove_discord_role_for_enrollment(enrollment)
            except:
                # Likely they left the server, handle this later
                pass
        except ObjectDoesNotExist:
            pass

        try:
            get_uid('github', user)
            remove_github_team_membership_for_enrollment(enrollment)
        except ObjectDoesNotExist:
            pass
        
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

def update_courses_from_quercus():

    for offering in Offering.objects.all():
        if offering.external_id is None:
            continue

        if not offering.active:
            continue
        
        # Look for an instructor Quercus token
        instructor = None
        for enrollment in offering.role_set.get(kind=Role.Kind.INSTRUCTOR) \
                                  .enrollment_set.all():
            try:
                enrollment.user.quercus_token
                instructor = enrollment.user
            except User.quercus_token.RelatedObjectDoesNotExist:
                pass

        assert instructor is not None
        api = QuercusRestAPI(instructor)
        quercus_course_id = offering.external_id
        students = api.list_students(quercus_course_id)
        _update(offering, students, Role.Kind.STUDENT)
        tas = api.list_tas(quercus_course_id)
        _update(offering, tas, Role.Kind.TA)
