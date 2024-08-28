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
        for student in api.list_students(quercus_course_id):
            username = student['sis_user_id']
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
            try:
                enrollment = Enrollment.objects.get(
                    user=user, role=student_role
                )
            except Enrollment.DoesNotExist:
                enrollment = Enrollment.objects.create(
                    user=user, role=student_role
                )

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
            except ObjectDoesNotExist:
                pass
