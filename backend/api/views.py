from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render

from django.contrib import auth
from django.contrib.auth.models import User

from compeng_gg.strategy import load_strategy
from social_django.utils import load_backend

from rest_framework import status
from rest_framework.response import Response

from rest_framework.decorators import api_view
from rest_framework import serializers

from django.views.decorators.csrf import csrf_exempt

from social_core.actions import do_complete
from social_core.exceptions import AuthForbidden

from rest_framework_simplejwt.tokens import RefreshToken

REDIRECT_URI = 'http://localhost:3000/auth/'

class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=512)

def discord_v0(request):
    serializer = CodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_404_NOT_FOUND)

    strategy = load_strategy(validated_data=serializer.validated_data)
    backend = load_backend(
        strategy=strategy, name='discord', redirect_uri=REDIRECT_URI
    )
    try:
        user = backend.auth_complete(
            strategy=strategy
        #    request=request, strategy=strategy, redirect_name=None
        )
    except AuthForbidden as e:
        return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    if not user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
def discord(request):
    if request.version == 'v0':
        return discord_v0(request)
    return HttpResponseNotFound()

def login_v0(request):
    username = request.data["username"]
    password = request.data["password"]

    if username is None or username == "":
        return JsonResponse({
            "errors": {"username": "Input username."},
        }, status=400)

    if password is None or password == "":
        return JsonResponse({
            "errors": {"password": "Input password."},
        }, status=400)

    if not User.objects.filter(username=username).exists():
        return JsonResponse({
            "errors": {"username": "Username does not exist."},
        }, status=400)

    user = auth.authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({
            "errors": {"password": "Wrong password."},
        }, status=400)

    auth.login(request, user)

    return JsonResponse({})

@api_view(['POST'])
def login(request):
    if request.version == 'v0':
        return login_v0(request)
    return HttpResponseNotFound()

def logout_v0(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=400)

    auth.logout(request)

    return JsonResponse({})

@api_view(['POST'])
def logout(request):
    if request.version == 'v0':
        return logout_v0(request)
    return HttpResponseNotFound()

def session_v0(request):
    if not request.user.is_authenticated:
        return JsonResponse({'is_authenticated': False}, status=401)

    return JsonResponse({
        'is_authenticated': True,
        'username': request.user.username,
    })

@api_view(['GET'])
def session(request):
    if request.version == 'v0':
        return session_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)

def self_v0(request):
    return Response({'username': request.user.username})

@api_view(['GET'])
def self(request):
    if request.version == 'v0':
        return self_v0(request)
    return Response(status=status.HTTP_404_NOT_FOUND)
