import datetime

from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from social_core.exceptions import (
    AuthAlreadyAssociated,
    AuthCanceled,
    AuthFailed,
    AuthForbidden,
    NotAllowedToDisconnect,
)

from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest_framework_simplejwt.tokens import RefreshToken

from compeng_gg.auth import auth_complete, disconnect
from compeng_gg.auth.serializers import CodeSerializer

from .serializers import UserSerializer

from threading import Thread

from courses.models import (
    Accommodation,
    Assignment,
    AssignmentResult,
    AssignmentTask,
    Course,
    Enrollment,
    Offering,
    Role,
    Semester,
)
from courses.utils import is_staff, sync_before_due_date

# TODO: with sqlite task.result is a dict, with postgres it's a str
def get_task_result(task):
    if type(task.result) is str and task.result != '':
        import json
        return json.loads(task.result)
    return task.result

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.prefetch_related('social_auth').order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_common(request, provider, allow_create_user=False):
    if request.user is None:
        return Response(
            {'detail': 'Already authenticated'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    try:
        user = auth_complete(
            provider, validated_data,
            allow_create_user=allow_create_user
        )
    except AuthAlreadyAssociated as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthCanceled as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthFailed as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if user is None:
        return Response(
            {'detail': 'No connected user found'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

def auth_discord(request):
    return auth_common(request, 'discord')

def auth_github(request):
    return auth_common(request, 'github')

def auth_google(request):
    return auth_common(request, 'google')

def auth_laforge(request):
    return auth_common(request, 'laforge', allow_create_user=True)

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def connect_common(request, provider):
    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    try:
        user = auth_complete(
            provider, validated_data,
            user=request.user,
            allow_create_user=False
        )
    except AuthAlreadyAssociated as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthCanceled as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthFailed as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()

def connect_discord(request):
    response = connect_common(request, 'discord')
    if response.status_code == 200:
        from discord_app.utils import add_to_discord_server
        user = request.user
        add_to_discord_server(user)
    return response

def connect_github(request):
    response = connect_common(request, 'github')
    if response.status_code == 200:
        from github_app.utils import add_github_team_membership, create_forks
        user = request.user
        add_github_team_membership(user)
        create_forks(user)
    return response

def connect_google(request):
    return connect_common(request, 'google')

def connect_laforge(request):
    return connect_common(request, 'laforge')

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def disconnect_common(request, provider):
    try:
        disconnect(provider, request.user)
    except NotAllowedToDisconnect as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response()

def disconnect_discord(request):
    return disconnect_common(request, 'discord')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def self(request):
    return Response({'username': request.user.username})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard(request):
    user = request.user
    offerings = []
    for enrollment in user.enrollment_set.all():
        offering = enrollment.role.offering
        if not offering.active:
            continue
        offerings.append({
            'name': str(offering),
            'slug': offering.course.slug,
            'role': str(enrollment.role),
        })
    failed_checks = []
    if not user.social_auth.filter(provider='discord').exists():
        failed_checks.append('connect-discord')
    if not user.social_auth.filter(provider='github').exists():
        failed_checks.append('connect-github')
    else:
        from github_app.utils import is_github_organization_member
        if not is_github_organization_member(user):
            failed_checks.append('join-github-organization')

    return Response({
        'username': user.username,
        'offerings': offerings,
        'failed-checks': failed_checks,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def settings(request):
    user = request.user
    data = {}
    for social_auth in user.social_auth.all():
        data[social_auth.provider] = social_auth.uid
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def tasks(request):
    data = []
    from runner.models import Task
    for task in Task.objects.all():
        push = task.push
        result = get_task_result(task)
        grade = result['grade'] if result and 'grade' in result else None

        task_data = {
            'id': task.id,
            'status': task.get_status_display(),
        }
        if not grade is None:
            task['grade'] = grade
        # Old style
        if task.push:
            push = task.push
            received = push.received
            task_data['repo'] = push.payload['repository']['name']
            task_data['commit'] = push.payload['after']
            task_data['received'] = received
        # New style
        if task.head_commit:
            head_commit = task.head_commit
            repository = head_commit.repository
            # TODO: check if this every returns more than one
            received = head_commit.pushes_head.all()[0].delivery.received
            task_data['repo'] = repository.name
            task_data['commit'] = head_commit.sha1
            task_data['received'] = received

        data.append(task_data)
    return Response(data)

def _get_assignment_data(assignment, user):
    due_date = assignment.due_date
    is_private_released = assignment.is_private_released
    # Look for accommodations
    try:
        accommodation = Accommodation.objects.get(
            user=user, assignment=assignment
        )
        due_date = accommodation.due_date
    except Accommodation.DoesNotExist:
        accommodation = None

    assignment_grade = 0
    tasks = []
    for assignment_task in assignment.assignmenttask_set.filter(
        user=user, assignment=assignment
    ).order_by('-task__created'):
        task = assignment_task.task
        result = get_task_result(task)
        grade = None
        before_due_date = assignment_task.before_due_date

        task_data = {
            'id': task.id,
            'status': task.get_status_display(),
            'result': result,
        }
        # Old style
        if task.push:
            push = task.push
            received = push.received
            task_data['repo'] = push.payload['repository']['name']
            task_data['commit'] = push.payload['after']
            task_data['received'] = received
        # New style
        if task.head_commit:
            head_commit = task.head_commit
            repository = head_commit.repository
            # TODO: check if this every returns more than one
            received = head_commit.pushes_head.all()[0].delivery.received
            task_data['repo'] = repository.name
            task_data['commit'] = head_commit.sha1
            task_data['received'] = received

        if not result is None and "tests" in result:
            if not is_private_released:
                # Filter out the tests
                result["tests"] = list(filter(lambda test: not "kind" in test or test["kind"] == "public", result["tests"]))
                grade = f"{assignment_task.public_grade}/{assignment.public_total} ({assignment.private_total} hidden)"
                if before_due_date and assignment_task.public_grade > assignment_grade:
                    assignment_grade = assignment_task.public_grade
            else:
                grade = f"{assignment_task.overall_grade}/{assignment.overall_total}"
                if before_due_date and assignment_task.overall_grade > assignment_grade:
                    assignment_grade = assignment_task.overall_grade

        if assignment.kind == Assignment.Kind.TESTS:
            if not grade is None:
                task_data['grade'] = grade
        elif assignment.kind == Assignment.Kind.LEADERBOARD:
            speedup = result['speedup'] if result and 'speedup' in result else None
            if speedup:
                task_data['speedup'] = speedup
        tasks.append(task_data)
        # on_time = received <= due_date
        # max_grade = 100 # TODO: This should probably come from the assign.
        # if accommodation and not on_time:
        #     if received > accommodation.due_date:
        #         continue
        #     if accommodation.max_grade:
        #         max_grade = accommodation.max_grade
        # elif not on_time:
        #     continue
        # if grade is None:
        #     continue
        # grade = min(grade, max_grade)
        # if grade > assignment_grade:
        #     assignment_grade = grade
    assignment_data = {
        'slug': assignment.slug,
        'name': assignment.name,
        'kind': assignment.kind,
        'due_date': due_date,
        'tasks': tasks,
    }
    # try:
    #     ag = AssignmentGrade.objects.get(user=user, assignment=assignment)
    #     if ag.grade > assignment_grade:
    #         assignment_grade = ag.grade
    #         assignment_data['grade'] = assignment_grade
    # except AssignmentGrade.DoesNotExist:
    #     pass
    if assignment.kind == Assignment.Kind.TESTS:
        if not is_private_released:
            assignment_data["raw_grade"] = assignment_grade
            assignment_data["grade"] = f"{assignment_grade:.1f}/{assignment.public_total:.1f} ({assignment.private_total:.1f} hidden)"
        else:
            assignment_data["raw_grade"] = assignment_grade
            assignment_data["grade"] = f"{assignment_grade:.1f}/{assignment.overall_total:.1f}"
    elif assignment.kind == Assignment.Kind.LEADERBOARD:
        leaderboard = []
        for entry in AssignmentLeaderboardEntry.objects.filter(assignment=assignment).order_by('-speedup'):
            entry_data = {'id': entry.user.id, 'speedup': entry.speedup}
            if entry.user.id == user.id:
                entry_data['highlight'] = True
            leaderboard.append(entry_data)
        assignment_data['leaderboard'] = leaderboard
    return assignment_data

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course(request, slug):
    from courses.models import Assignment, AssignmentLeaderboardEntry, AssignmentGrade
    user = request.user
    try:
        offering = Offering.objects.get(course__slug=slug, active=True)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # TODO: archive offerings
    #except Offering.MultipleObjectsReturned:
    #    offering = Offering.objects.get(course__slug=slug, active=True)

    data = {
        'name': str(offering),
        "is_staff": is_staff(user, offering),
    }
    assignments = []
    for assignment in offering.assignment_set.all():
        assignment_data = _get_assignment_data(assignment, user)
        assignments.append(assignment_data)
    data['assignments'] = assignments
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def staff(request, course_slug):
    user = request.user
    try:
        offering = Offering.objects.get(active=True, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
    data = {
        "offering": str(offering),
        "course_slug": course_slug,
        "semester_slug": offering.slug,
        "is_quercus_added": offering.external_id is not None
    }
    assignments = []
    for assignment in offering.assignment_set.all():
        assignment_data = {
            "slug": assignment.slug,
            "name": assignment.name,
            "due_date": assignment.due_date,
        }
        assignments.append(assignment_data)
    data["assignments"] = assignments
    return Response(data)

def _staff_assignment_student_data(assignment, enrollment):
    user = enrollment.user
    repository = enrollment.student_repo
    submissions = AssignmentTask.objects.filter(user=user, assignment=assignment, before_due_date=True).count()
    late_submissions = AssignmentTask.objects.filter(user=user, assignment=assignment, before_due_date=False).count()
    overall_grade = 0
    graded_commit_url = ""
    try:
        assignment_result = AssignmentResult.objects.get(user=user, assignment=assignment)
        task = assignment_result.task
        # No sure why this disappeared?
        if not task.head_commit is None:
            graded_commit_url = f"https://github.com/{repository.full_name}/tree/{task.head_commit.sha1}"
        overall_grade = assignment_result.overall_grade
    except AssignmentResult.DoesNotExist:
        pass
    accommodation_days = 0
    try:
        accommodation = Accommodation.objects.get(user=user, assignment=assignment)
        accommodation_days = (accommodation.due_date - assignment.due_date).days
    except Accommodation.DoesNotExist:
        pass
    return {
        "username": user.username,
        "repository_name": repository.name if repository else "",
        "repository_url": f"https://github.com/{repository.full_name}" if repository else "",
        "overall_grade": overall_grade,
        "graded_commit_url": graded_commit_url,
        "submissions": submissions,
        "late_submissions": late_submissions,
        "accommodation": accommodation_days,
    }

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def staff_assignment(request, course_slug, assignment_slug):
    user = request.user
    try:
        offering = Offering.objects.get(active=True, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        assignment = Assignment.objects.get(offering=offering, slug=assignment_slug)
    except Assignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
    data = {
        "offering": str(offering),
        "slug": assignment.slug,
        "name": assignment.name,
        "is_private_released": assignment.is_private_released,
    }

    students_with_submissions_count = 0
    students_count = 0
    students_data = []
    for enrollment in Enrollment.objects.filter(role=student_role).order_by("user__username"):
        # TODO: skip if there's no student repo
        if enrollment.student_repo is None:
            # TODO, why does this happen now?
            continue
        student_data = _staff_assignment_student_data(assignment, enrollment)
        if student_data["submissions"] > 0:
            students_with_submissions_count += 1
        students_count += 1
        students_data.append(student_data)
    data["students"] = students_data
    data["students_with_submissions_count"] = students_with_submissions_count
    data["students_count"] = students_count
    return Response(data)

class IsPrivateReleasedSerializer(serializers.Serializer):
    is_private_released = serializers.BooleanField()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def staff_assignment_student(request, course_slug, assignment_slug, student_username):
    user = request.user
    try:
        offering = Offering.objects.get(active=True, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        assignment = Assignment.objects.get(offering=offering, slug=assignment_slug)
    except Assignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        student_user = User.objects.get(username=student_username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)

    try:
        enrollment = Enrollment.objects.get(user=student_user, role=student_role)
    except Enrollment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    assignment_data = _get_assignment_data(assignment, student_user)

    return Response(assignment_data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def staff_assignment_private_release(request, course_slug, assignment_slug):
    user = request.user
    try:
        offering = Offering.objects.get(active=True, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        assignment = Assignment.objects.get(offering=offering, slug=assignment_slug)
    except Assignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = IsPrivateReleasedSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    assignment.is_private_released = validated_data["is_private_released"]
    assignment.save()

    from quercus_app.utils import sync_assignment_to_quercus
    sync_assignment_to_quercus(assignment)

    return Response()

class AccommodationSerializer(serializers.Serializer):
    username = serializers.CharField()
    days = serializers.IntegerField()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def staff_assignment_accommodation(request, course_slug, assignment_slug):
    user = request.user
    try:
        offering = Offering.objects.get(active=True, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        assignment = Assignment.objects.get(offering=offering, slug=assignment_slug)
    except Assignment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AccommodationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    try:
        user = User.objects.get(username=validated_data["username"])
    except User.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    days = validated_data["days"]

    # TODO
    if days > 0:
        due_date = assignment.due_date + datetime.timedelta(days=days)
        try:
            accommodation = Accommodation.objects.get(user=user, assignment=assignment)
            accommodation.due_date = due_date
            accommodation.save()
        except Accommodation.DoesNotExist:
            Accommodation.objects.create(user=user, assignment=assignment, due_date=due_date)
    elif days == 0:
        try:
            accommodation = Accommodation.objects.get(user=user, assignment=assignment)
            accommodation.delete()
        except Accommodation.DoesNotExist:
            pass

    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
    enrollment = Enrollment.objects.get(user=user, role__offering=offering)
    # Reset the assignment result to re-compute
    try:
        assignment_result = AssignmentResult.objects.get(user=user, assignment=assignment)
        assignment_result.delete()
    except AssignmentResult.DoesNotExist:
        pass
    for assignment_task in AssignmentTask.objects.filter(user=user, assignment=assignment):
        sync_before_due_date(assignment_task)

    return Response(_staff_assignment_student_data(assignment, enrollment))

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def students(request, slug):
    user = request.user
    offering = Offering.objects.get(active=True, course__slug=slug)
    instructor_role = Role.objects.get(offering=offering, kind=Role.Kind.INSTRUCTOR)
    try:
        Enrollment.objects.get(user=user, role=instructor_role)
    except Enrollment.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
    return Response([e.user.username for e in Enrollment.objects.filter(role=student_role)])

class DateSerializer(serializers.Serializer):
    date = serializers.DateField()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def students_commits(request, slug):
    import zoneinfo
    from social_django.models import UserSocialAuth
    from compeng_gg.django.github.models import Delivery, Push
    from compeng_gg.django.github.models import User as GitHubUser
    from django.contrib.contenttypes.models import ContentType

    user = request.user
    offering = Offering.objects.get(active=True, course__slug=slug)
    instructor_role = Role.objects.get(offering=offering, kind=Role.Kind.INSTRUCTOR)
    try:
        Enrollment.objects.get(user=user, role=instructor_role)
    except Enrollment.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = DateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data
    date = validated_data["date"]

    toronto_tz = zoneinfo.ZoneInfo("America/Toronto")
    cutoff = datetime.datetime.combine(
        date, datetime.datetime.max.time(), tzinfo=toronto_tz
    )
    content_type = ContentType.objects.get_for_model(Push)

    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
    data = []
    for e in Enrollment.objects.filter(role=student_role):
        user = e.user
        received = None
        sha1 = None
        try:
            social = UserSocialAuth.objects.get(user=user, provider='github')
            login = social.extra_data["login"]
            github_user = GitHubUser.objects.get(login=login)
            latest_delivery = Delivery.objects.filter(received__lte=cutoff, content_type=content_type, object_id__in=github_user.pushes.all()).order_by('-received')[0]
            received = latest_delivery.received.astimezone(toronto_tz)
            sha1 = latest_delivery.push.head_commit.sha1
        except:
            pass
        data.append({
            "username": user.username,
            "sha1": sha1,
            "received": received,
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def offerings(request):
    user = request.user
    offerings = []
    for enrollment in user.enrollment_set.all():
        offering = enrollment.role.offering
        if not offering.active:
            continue
        offerings.append({
            'name': str(offering),
            'slug': offering.course.slug,
            'role': str(enrollment.role),
        })
    return Response(offerings)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def semesters(request):
    semesters = []
    for semester in Semester.objects.all():
        courses = []
        for course in Course.objects.all():
            if Offering.objects.filter(course__slug=course.slug, slug=semester.slug).exists():
                continue
            courses.append({
                'name': course.name,
                'slug': course.slug,
            })
        semesters.append({
            'name': semester.name,
            'slug': semester.slug,
            'courses': courses,

        })
    return Response(semesters)

def generate_ssh_key():
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        id_ed25519_path = f"{tmp_dir}/id_ed25519"
        id_ed25519_pub_path = f"{tmp_dir}/id_ed25519.pub"
        p = subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", id_ed25519_path, "-N", "", "-C", ""],
            capture_output=True,
            text=True,
            check=True,
        )
        with open(id_ed25519_path) as f:
            id_ed25519 = f.read()
        with open(id_ed25519_pub_path) as f:
            id_ed25519_pub = f.read()
    return id_ed25519, id_ed25519_pub

def create_staff_only_repo(api, name, instructor_role, ta_role):
    api.create_org_repo_for_org(name)
    api.add_team_repository_permissions_for_org(
        instructor_role.github_team_slug,
        name,
        permission='push'
    )
    api.add_team_repository_permissions_for_org(
        ta_role.github_team_slug,
        name,
        permission='push'
    )

def create_offering_repos(offering):
    import json
    import subprocess

    from github_app.rest_api import GitHubRestAPI
    api = GitHubRestAPI()

    instructor_role = Role.objects.get(offering=offering, kind=Role.Kind.INSTRUCTOR)
    ta_role = Role.objects.get(offering=offering, kind=Role.Kind.TA)
    student_role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)

    student_repo_name = f"{offering.slug}-{offering.course.slug}-student"
    api.create_org_repo_for_org(student_repo_name)
    api.add_team_repository_permissions_for_org(
        instructor_role.github_team_slug,
        student_repo_name,
        permission='push'
    )
    api.add_team_repository_permissions_for_org(
        ta_role.github_team_slug,
        student_repo_name,
        permission='push'
    )
    api.add_team_repository_permissions_for_org(
        student_role.github_team_slug,
        student_repo_name,
        permission='pull'
    )

    docs_repo_name = f"{offering.slug}-{offering.course.slug}-docs"
    create_staff_only_repo(api, docs_repo_name, instructor_role, ta_role)
    api.create_github_pages_for_org(docs_repo_name)

    staff_repo_name = f"{offering.slug}-{offering.course.slug}-staff"
    create_staff_only_repo(api, staff_repo_name, instructor_role, ta_role)

    runner_repo_name = f"{offering.slug}-{offering.course.slug}-runner"
    create_staff_only_repo(api, runner_repo_name, instructor_role, ta_role)

    id_ed25519, id_ed25519_pub = generate_ssh_key()

    secret_name = f"{runner_repo_name}-deploy"
    namespace = "compeng"

    secret_data = {
        "apiVersion": "v1",
        "kind": "Secret",
        "type": "Opaque",
        "metadata": {
            "name": secret_name,
            "namespace": namespace,
        },
        "stringData": {
            "config": "Host github.com\n  StrictHostKeyChecking no\n  UserKnownHostsFile=/dev/null\n",
            "id_ed25519": id_ed25519,
            "id_ed25519.pub": id_ed25519_pub,
        },
    }
    p = subprocess.run(
        ["kubectl", "create", "-f", "-"],
        check=True, input=json.dumps(secret_data), text=True
    )

    api.create_deploy_key_for_org(runner_repo_name, id_ed25519_pub)

class CreateOfferingSerializer(serializers.Serializer):
    course_slug = serializers.CharField()
    semester_slug = serializers.CharField()
    instructor = serializers.CharField()

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_offering(request):
    serializer = CreateOfferingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    semester_slug = validated_data['semester_slug']
    course_slug = validated_data['course_slug']
    instructor = validated_data['instructor']

    try:
        semester = Semester.objects.get(slug=semester_slug)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(slug=course_slug)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=instructor)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    offering = Offering.objects.create(
        course=course,
        slug=semester.slug,
        name=semester.name,
        start=semester.start,
        end=semester.end,
        active=True,
    )

    from courses.management.commands.coursestestmodels import create_default_roles, create_discord_roles, create_github_teams
    from discord_app.rest_api import DiscordRestAPI

    create_default_roles(offering)
    create_discord_roles(
        offering,
        student_color=DiscordRestAPI.COLOR_BLUE
    )
    create_github_teams(offering)

    instructor_role = Role.objects.get(offering=offering, kind=Role.Kind.INSTRUCTOR)
    Enrollment.objects.create(role=instructor_role, user=user)

    create_offering_repos(offering)

    return Response(status=status.HTTP_201_CREATED)

class CreateAssignmentSerializer(serializers.Serializer):
    course_slug = serializers.CharField()
    semester_slug = serializers.CharField()
    slug = serializers.CharField()
    name = serializers.CharField()
    due_date = serializers.DateTimeField()
    files = serializers.JSONField()
    public_total = serializers.FloatField()
    private_total = serializers.FloatField()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_assignment(request):

    serializer = CreateAssignmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    course_slug = validated_data["course_slug"]
    semester_slug = validated_data["semester_slug"]

    try:
        offering = Offering.objects.get(slug=semester_slug, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    public_total = validated_data["public_total"]
    private_total = validated_data["private_total"]
    overall_total = public_total + private_total

    assignment = Assignment.objects.create(
        offering=offering,
        kind=Assignment.Kind.TESTS,
        slug=validated_data["slug"],
        name=validated_data["name"],
        due_date=validated_data["due_date"],
        files=validated_data["files"],
        public_total=public_total,
        private_total=private_total,
        overall_total=overall_total,
    )

    return Response(status=status.HTTP_201_CREATED)

class AdddQuercusIdSerializer(serializers.Serializer):
    course_slug = serializers.CharField()
    semester_slug = serializers.CharField()
    quercus_id = serializers.IntegerField()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_quercus_id(request):

    serializer = AdddQuercusIdSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    course_slug = validated_data["course_slug"]
    semester_slug = validated_data["semester_slug"]

    try:
        offering = Offering.objects.get(slug=semester_slug, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    offering.external_id = validated_data["quercus_id"]
    offering.save()

    return Response(status=status.HTTP_201_CREATED)

class SyncQuercusSerializer(serializers.Serializer):
    course_slug = serializers.CharField()
    semester_slug = serializers.CharField()

def sync_quercus_run(offering):
    from quercus_app.utils import update_offering_from_quercus
    update_offering_from_quercus(offering)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_quercus(request):

    serializer = SyncQuercusSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.validated_data

    course_slug = validated_data["course_slug"]
    semester_slug = validated_data["semester_slug"]

    try:
        offering = Offering.objects.get(slug=semester_slug, course__slug=course_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if not is_staff(user, offering):
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if offering.external_id is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    Thread(target=sync_quercus_run, args=(offering,)).start()

    return Response(status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    return Response({
        'login': reverse('login', request=request, format=format),
    })
