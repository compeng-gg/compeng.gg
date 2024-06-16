from django.contrib import auth
from django.contrib.auth.models import User

from social_core.actions import do_complete
from social_core.exceptions import AuthForbidden, AuthCanceled
from compeng_gg.strategy import load_strategy, load_no_create_user_strategy
from social_django.utils import load_backend
from social_django.models import UserSocialAuth

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

REDIRECT_URI = 'http://localhost:3000/auth/'

class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=512)

def auth_common(request, backend_name, strategy_func):
    if request.user.is_authenticated:
        return Response(
            {'detail': 'Already authenticated'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    strategy = strategy_func(validated_data=serializer.validated_data)
    backend = load_backend(
        strategy=strategy, name=backend_name, redirect_uri=REDIRECT_URI
    )
    try:
        user = backend.auth_complete(
            strategy=strategy
        #    request=request, strategy=strategy, redirect_name=None
        )
    except AuthCanceled as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not user:
        return Response(
            {'detail': 'No connected user found'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

def auth(request, backend_name):
    return auth_common(request, backend_name, load_strategy)

def auth_no_create_user(request, backend_name):
    return auth_common(request, backend_name, load_no_create_user_strategy)

def connect(request, backend_name):
    if not request.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    strategy = load_no_create_user_strategy(
        validated_data=serializer.validated_data
    )
    backend = load_backend(
        strategy=strategy, name=backend_name, redirect_uri=REDIRECT_URI
    )
    try:
        user = backend.auth_complete(
            strategy=strategy,
            user=request.user,
        #    request=request, strategy=strategy, redirect_name=None
        )
    except AuthCanceled as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not user:
        return Response(
            {'detail': 'No connected user found'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    refresh = RefreshToken.for_user(user)
    return Response()

def auth_discord_v0(request):
    return auth_no_create_user(request, 'discord')

@api_view(['POST'])
@permission_classes([AllowAny])
def auth_discord(request):
    if request.version == 'v0':
        return auth_discord_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)

def self_v0(request):
    return Response({'username': request.user.username})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def self(request):
    if request.version == 'v0':
        return self_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)

def connect_discord_v0(request):
    return connect(request, 'discord')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_discord(request):
    if request.version == 'v0':
        return connect_discord_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)

def settings_v0(request):
    user = request.user
    data = {}
    for social_auth in user.social_auth.all():
        data[social_auth.provider] = social_auth.uid
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settings(request):
    if request.version == 'v0':
        return settings_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)
