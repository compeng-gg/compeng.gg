from django.contrib.auth.models import User
from courses.models import Enrollment, Role
from github_app.models import Push

def get_data_for_push(push):
    data = {}

    name = push.payload['repository']['name']
    ece344_prefix = '2024-fall-ece344-'

    if name.startswith(ece344_prefix):
        username = name[len(ece344_prefix):]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return data
        data['user'] = user
        role = Role.objects.get(
            kind=Role.Kind.STUDENT, offering__course__slug='ece344'
        )
        try:
            enrollment = Enrollment.objects.get(user=user, role=role)
        except Enrollment.DoesNotExist:
            return data
        data['enrollment'] = enrollment

        offering = role.offering
        assignments = []
        for assignment in offering.assignment_set.all():
            files = assignment.files
            found = False
            for commit in push.payload['commits']:
                for modified_file in commit['modified']:
                    if modified_file in files:
                        found = True
                        assignments.append(assignment)
                        break
                if found:
                    break
        data['assignments'] = assignments

    return data