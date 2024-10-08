from django.contrib.auth.models import User
from courses.models import Enrollment, Role
from github_app.models import Push

def get_data_for_push(push):
    data = {}

    name = push.payload['repository']['name']
    ece344_prefix = '2024-fall-ece344-'
    ece454_prefix = '2024-fall-ece454-'

    # TODO, this should be a lot better
    if not (name.startswith(ece344_prefix) or name.startswith(ece454_prefix)):
        return data

    username = name[len(ece344_prefix):]
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return data
    data['user'] = user
    if name.startswith(ece344_prefix):
        role = Role.objects.get(
            kind=Role.Kind.STUDENT, offering__course__slug='ece344'
        )
    elif name.startswith(ece454_prefix):
        role = Role.objects.get(
            kind=Role.Kind.STUDENT, offering__course__slug='ece454'
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