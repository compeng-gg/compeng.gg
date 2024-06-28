from django import conf
from django.contrib import auth
from django.contrib.auth.models import User

from social_core.actions import do_complete
from social_core.exceptions import (
    AuthAlreadyAssociated,
    AuthForbidden,
    AuthCanceled,
    NotAllowedToDisconnect,
)

from social_django.utils import load_backend
from social_django.models import UserSocialAuth

from compeng_gg.strategy import load_strategy, load_no_create_user_strategy

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=512)

def psa_common(request, backend_name, strategy_func, user=None):
    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    strategy = strategy_func(validated_data=serializer.validated_data)
    backend = load_backend(
        strategy=strategy, name=backend_name,
        redirect_uri=conf.settings.AUTH_REDIRECT_URI,
    )
    try:
        print('auth complete start', user)
        user_result = backend.auth_complete(
            strategy=strategy,
            user=user,
        )
        print('auth complete end', user_result)
        if user_result:
            print('user social auth:', user_result.social_auth.all())
    except AuthAlreadyAssociated as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthCanceled as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return user_result

def auth_common(request, backend_name, strategy_func):
    if request.user.is_authenticated:
        return Response(
            {'detail': 'Already authenticated'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = psa_common(request, backend_name, strategy_func)
    if isinstance(result, Response):
        return result
    user = result

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
    if not request.user or not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    result = psa_common(request, backend_name, load_no_create_user_strategy,
                        user=request.user)
    if isinstance(result, Response):
        return result
    user = result

    assert(request.user == user)

    return Response()

def disconnect(request, backend_name):
    if not request.user or not request.user.is_authenticated:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    strategy = load_no_create_user_strategy()
    backend = load_backend(
        strategy=strategy, name=backend_name, redirect_uri=None,
    )

    try:
        backend.disconnect(user=request.user)
    except NotAllowedToDisconnect as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

def disconnect_discord_v0(request):
    return disconnect(request, 'discord')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def disconnect_discord(request):
    if request.version == 'v0':
        return disconnect_discord_v0(request)
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
