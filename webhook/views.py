import json

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models
from .socket import send_task

@csrf_exempt
def endpoint(request):
    if request.method != "POST":
        raise Http404()

    if not 'X-Gitlab-Token' in request.headers \
       or request.headers['X-Gitlab-Token'] != settings.QUEUE_SECRET_TOKEN:
        return HttpResponse(status=401)

    if not 'X-Gitlab-Event' in request.headers \
       or request.headers['X-Gitlab-Event'] != 'Push Hook':
        return HttpResponse(status=400)

    if request.headers['Content-Type'] != 'application/json':
        return HttpResponse(status=400)

    try:
        data = json.load(request)
        if data['object_kind'] != 'push' or data['event_name'] != 'push':
            return HttpResponse(status=400)

        task = models.Task.objects.create(
            status=models.Task.Status.QUEUED,
            data=data,
        )
    except:
        return HttpResponse(status=400)

    try:
        send_task(task)
    except:
        pass

    return HttpResponse(status=200)
