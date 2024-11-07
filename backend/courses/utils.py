from django.contrib.auth.models import User
from courses.models import Enrollment, Role, Accommodation, Assignment
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

def get_grade_for_assignment(user, assignment):
    from api.v0.views import get_task_result
    due_date = assignment.due_date
    # Look for accommodations
    try:
        accommodation = Accommodation.objects.get(
            user=user, assignment=assignment
        )
    except Accommodation.DoesNotExist:
        accommodation = None
    assignment_grade = 0
    tasks = []
    for assignment_task in assignment.assignmenttask_set.filter(
        user=user, assignment=assignment
    ).order_by('-task__created'):
        task = assignment_task.task
        push = task.push
        result = get_task_result(task)
        grade = result['grade'] if result and 'grade' in result else None
        if assignment.kind == Assignment.Kind.TESTS:
            pass
        elif assignment.kind == Assignment.Kind.LEADERBOARD:
            speedup = result['speedup'] if result and 'speedup' in result else None
            if speedup:
                if speedup > 985:
                    grade = 100
                elif speedup > 885:
                    grade = 98
                elif speedup > 785:
                    grade = 96
                elif speedup > 685:
                    grade = 94
                elif speedup > 585:
                    grade = 92
                elif speedup > 485:
                    grade = 90
                elif speedup > 385:
                    grade = 88
                elif speedup > 285:
                    grade = 86
                elif speedup > 185:
                    grade = 84
                elif speedup > 85:
                    grade = 82
        on_time = push.received <= due_date
        max_grade = 100 # TODO: This should probably come from the assign.
        if accommodation and not on_time:
            if push.received > accommodation.due_date:
                continue
            if accommodation.max_grade:
                max_grade = accommodation.max_grade
        elif not on_time:
            continue
        if grade is None:
            continue
        grade = min(grade, max_grade)
        if grade > assignment_grade:
            assignment_grade = grade
    return assignment_grade
