from django.shortcuts import render

from rest_framework.decorators import api_view

from django.http import HttpResponseNotFound, JsonResponse
from django.contrib import auth

def login_v0(request):
    username = request.data['username']
    password = request.data['password']

    if username is None or password is None:
        return JsonResponse({'error': 'Input username or password'}, status=400)

    user = auth.authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'Wrong username or password'}, status=400)

    auth.login(request, user)

    return JsonResponse({'success': 'You are logged in'})

@api_view(['POST'])
def login(request):
    if request.version == 'v0':
        return login_v0(request)
    return HttpResponseNotFound()

def logout_v0(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Already logged out'}, status=400)

    auth.logout(request)

    return JsonResponse({'success': 'You are logged out'})

@api_view(['POST'])
def logout(request):
    if request.version == 'v0':
        return logout_v0(request)
    return HttpResponseNotFound()

def session_v0(request):
    if not request.user.is_authenticated:
        return JsonResponse({'is_authenticated': False})

    return JsonResponse({'is_authenticated': True})

@api_view(['POST'])
def session(request):
    if request.version == 'v0':
        return session_v0(request)
    return HttpResponseNotFound()
