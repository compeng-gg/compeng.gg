import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models
from .socket import send_task

@csrf_exempt
def webhook(request):
    if request.method != "POST":
        return HttpResponse(status=401)

    if not 'X-Gitlab-Token' in request.headers:
        return HttpResponse(status=401)

    if request.headers['X-Gitlab-Token'] != settings.ANALYZER_SECRET_TOKEN:
        return HttpResponse(status=401)

    if request.headers['Content-Type'] != 'application/json':
        return HttpResponse(status=400)

    try:
        data = json.load(request)
    except:
        return HttpResponse(status=400)

    task = models.Task.objects.create(
        project_id=data['project_id'],
        ref=data['ref'],
        before=data['before'],
        after=data['after'],
        status=models.Task.Status.QUEUED
    )
    try:
        send_task(task)
    except:
        pass

    return HttpResponse(status=200)
