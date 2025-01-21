from compeng_gg.auth import get_uid
from courses.models import (
    Accommodation,
    Assignment,
    AssignmentTask,
    AssignmentResult,
    Enrollment,
    Role,
)
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from runner.models import Runner, Task
from runner.utils import create_k8s_task

from discord_app.utils import add_discord_role_for_enrollment
from github_app.utils import add_github_team_membership_for_enrollment, create_fork_for_enrollment

def is_staff(user, offering):
    instructor_role = Role.objects.get(offering=offering, kind=Role.Kind.INSTRUCTOR)
    ta_role = Role.objects.get(offering=offering, kind=Role.Kind.TA)
    try:
        Enrollment.objects.get(user=user, role__in=[instructor_role, ta_role])
        return True
    except Enrollment.DoesNotExist:
        return False

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

# Also sets AssignmentResult
def sync_before_due_date(assignment_task):
    task = assignment_task.task
    if not task.head_commit:
        return
    head_commit = task.head_commit
    repository = head_commit.repository
    # TODO: check if this every returns more than one
    received = head_commit.pushes_head.all()[0].delivery.received

    user = assignment_task.user
    assignment = assignment_task.assignment 
    due_date = assignment.due_date
    try:
        accommodation = Accommodation.objects.get(
            user=user, assignment=assignment
        )
        due_date = accommodation.due_date
    except Accommodation.DoesNotExist:
        pass

    if received <= due_date:
        assignment_task.before_due_date = True
    else:
        assignment_task.before_due_date = False
    assignment_task.save()

    # Only update the assignment result if it's before the due date
    if assignment_task.before_due_date and not assignment_task.overall_grade is None:
        try:
            assignment_result = AssignmentResult.objects.get(user=user, assignment=assignment)
            if assignment_task.before_due_date and assignment_task.overall_grade > assignment_result.overall_grade:
                assignment_result.public_grade = assignment_task.public_grade
                assignment_result.private_grade = assignment_task.private_grade
                assignment_result.overall_grade = assignment_task.overall_grade
                assignment_result.task = task
                assignment_result.save()
        except AssignmentResult.DoesNotExist:
            assignment_result = AssignmentResult.objects.create(
                user=user, assignment=assignment,
                public_grade=assignment_task.public_grade,
                private_grade=assignment_task.private_grade,
                overall_grade=assignment_task.overall_grade,
                task=task,
            )

# This is called from runrunner after the task completes
def populate_assignment_grades(task):
    from api.v0.views import get_task_result
    for assignment_task in task.assignmenttask_set.all():
        result = get_task_result(task)
        if result is None or not "tests" in result:
            continue
        public_grade = 0.0
        private_grade = 0.0
        for test in result["tests"]:
            weight = test["weight"]
            if test["result"] != "OK":
                # Failing a weight of 0.0 invalidates the grade.
                if weight == 0.0:
                    public_grade = 0.0
                    private_grade = 0.0
                    break
                continue
            if not "kind" in test or test["kind"] != "private":
                public_grade += weight
            else:
                private_grade += weight
        overall_grade = public_grade + private_grade
        assert result["grade"] == overall_grade
        assignment_task.public_grade = public_grade
        assignment_task.private_grade = private_grade
        assignment_task.overall_grade = overall_grade
        assignment_task.save()

        sync_before_due_date(assignment_task)
