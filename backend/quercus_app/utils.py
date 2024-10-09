from compeng_gg.auth import get_uid
from courses.models import Offering, Institution, Member, Role, Enrollment
from discord_app.utils import add_discord_role_for_enrollment
from github_app.utils import add_github_team_membership_for_enrollment
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from quercus_app.models import QuercusUser
from quercus_app.rest_api import QuercusRestAPI

def update_courses_from_quercus():
    utoronto = Institution.objects.get(slug='utoronto')

    for offering in Offering.objects.all():
        if offering.external_id is None:
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

        student_role = offering.role_set.get(kind=Role.Kind.STUDENT)

        quercus_course_id = offering.external_id
        students = api.list_students(quercus_course_id)
        print(f'Got {len(students)} students')
        for student in students:
            username = student['sis_user_id']
            # Likely the test student
            if username is None:
                continue
            quercus_user_id = student['id']
            student_id = int(student['integration_id'])
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

            enrollment, enrollment_created = Enrollment.objects.get_or_create(
                user=user, role=student_role
            )
            if not enrollment_created:
                continue

            print('Adding', user.username)

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
                offering = enrollment.role.offering
                from github_app.utils import create_fork
                create_fork(offering.slug, user)
            except ObjectDoesNotExist:
                pass
