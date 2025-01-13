from compeng_gg.auth import get_uid
from courses.models import Enrollment, Role, Accommodation, Assignment, AssignmentTask
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from runner.models import Runner, Task
from runner.utils import create_k8s_task

from discord_app.utils import add_discord_role_for_enrollment
from github_app.utils import add_github_team_membership_for_enrollment, create_fork_for_enrollment

def has_change_for_assignment(push, assignment):
    raw_files = list(assignment.files)
    files = list(filter(lambda x: not x.endswith('/'), raw_files))
    dirs = list(filter(lambda x: x.endswith('/'), raw_files))
    for commit in push.commits.all():
        for path in commit.paths_added.all():
            if path.relative in files:
                return True
            for d in dirs:
                if path.relative.startswith(d):
                    return True
        for path in commit.paths_modified.all():
            if path.relative in files:
                return True
            for d in dirs:
                if path.relative.startswith(d):
                    return True
    return False

def create_course_tasks(push):
    if not settings.RUNNER_USE_K8S:
        return

    repository = push.repository
    try:
        enrollment = repository.enrollment
    except ObjectDoesNotExist:
        return
    user = enrollment.user
    role = enrollment.role
    offering = role.offering

    if not offering.runner_repo:
        return

    assignments = []
    for assignment in offering.assignment_set.all():
        if not has_change_for_assignment(push, assignment):
            continue

        image = f"{offering.runner_repo.name}:latest"
        command = f"/workspace/{assignment.slug}/grade.py"
        runner, _ = Runner.objects.get_or_create(image=image, command=command)

        task = Task.objects.create(
            runner=runner,
            status=Task.Status.QUEUED,
            head_commit=push.head_commit,
        )
        assignment_task = AssignmentTask.objects.create(
            user=user,
            assignment=assignment,
            task=task,
        )

        create_k8s_task(task)

def add_enrollment(user, offering, role_kind):
    role = Role.objects.get(offering=offering, kind=role_kind)
    enrollment, created = Enrollment.objects.get_or_create(user=user, role=role)

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

def get_data_for_old_push(push):
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
        raw_files = list(assignment.files)
        files = list(filter(lambda x: not x.endswith('/'), raw_files))
        dirs = list(filter(lambda x: x.endswith('/'), raw_files))
        found = False
        for commit in push.payload['commits']:
            for modified_file in commit['modified']:
                if modified_file in files:
                    found = True
                    assignments.append(assignment)
                    break
                for d in dirs:
                    if modified_file.startswith(d):
                        found = True
                        assignments.append(assignment)
                        break
                if found:
                    break
            if found:
                break

            for added_file in commit['added']:
                for d in dirs:
                    if added_file.startswith(d):
                        found = True
                        assignments.append(assignment)
                        break
                if found:
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
