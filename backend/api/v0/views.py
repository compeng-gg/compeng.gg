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

from courses.models import (
    Accommodation,
    Assignment,
    AssignmentResult,
    AssignmentTask,
    Enrollment,
    Offering,
    Role,
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
                grade = f"{assignment_task.public_grade:.0f}/{assignment.public_total:.0f} ({assignment.private_total:.0f} hidden)"
                if before_due_date and assignment_task.public_grade > assignment_grade:
                    assignment_grade = assignment_task.public_grade
            else:
                grade = f"{assignment_task.overall_grade:.0f}/{assignment.overall_total:.0f}"
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
            assignment_data["grade"] = f"{assignment_grade:.0f}/{assignment.public_total:.0f} ({assignment.private_total:.0f} hidden)"
        else:
            assignment_data["grade"] = f"{assignment_grade:.0f}/{assignment.overall_total:.0f}"
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
        offering = Offering.objects.get(course__slug=slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Offering.MultipleObjectsReturned:
        offering = Offering.objects.get(course__slug=slug, active=True)

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

    return assignment_data

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
        offerings.append({
            'name': str(offering),
            'slug': offering.course.slug,
            'role': str(enrollment.role),
        })
    return Response(offerings)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    return Response({
        'login': reverse('login', request=request, format=format),
    })
