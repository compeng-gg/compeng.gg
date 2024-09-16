from django.contrib.auth.models import User

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
        from github_app.utils import add_github_team_membership, create_fork
        user = request.user
        add_github_team_membership(user)
        create_fork('ece344', user)
        create_fork('ece454', user)
    return response

def connect_google(request):
    return connect_common(request, 'google')

def connect_laforge(request):
    return connect_common(request, 'laforge')

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
        data.append({
            'id': task.id,
            'status': task.get_status_display(),
            'grade': grade,
            'repo': push.payload['repository']['name'],
            'commit': push.payload['after'],
            'received': push.received,
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def course(request, slug):
    from courses.models import Offering
    try:
        offering = Offering.objects.get(course__slug=slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {
        'name': str(offering),
    }
    assignments = []
    for assignment in offering.assignment_set.all():
        due_date = assignment.due_date
        assignment_grade = 0
        tasks = []
        for assignment_task in assignment.assignmenttask_set.filter(
            user=request.user, assignment=assignment
        ).order_by('-task__created'):
            task = assignment_task.task
            push = task.push
            result = get_task_result(task)
            grade = result['grade'] if result and 'grade' in result else None
            tasks.append({
                'id': task.id,
                'status': task.get_status_display(),
                'grade': grade,
                'repo': push.payload['repository']['name'],
                'commit': push.payload['after'],
                'received': push.received,
                'result': task.result,
            })
            if push.received > due_date:
                continue
            if grade is None:
                continue
            if grade > assignment_grade:
                assignment_grade = grade
        assignments.append({
            'slug': assignment.slug,
            'name': assignment.name,
            'due_date': assignment.due_date,
            'grade': assignment_grade,
            'tasks': tasks,
        })
    data['assignments'] = assignments
    print(data)
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
