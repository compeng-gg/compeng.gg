from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render

from django.contrib import auth
from django.contrib.auth.models import User

from rest_framework.decorators import api_view

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
    return HttpResponseNotFound()
