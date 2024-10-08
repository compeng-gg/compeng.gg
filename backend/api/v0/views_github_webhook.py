from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import hashlib
import hmac
import json

from courses.models import AssignmentTask
from courses.utils import get_data_for_push
from django.conf import settings
from django.contrib.auth.models import User
from github_app.models import Push
from runner.models import Task
from runner.socket import send_task

def create_tasks(push):
    data = get_data_for_push(push)
    if not 'assignments' in data:
        return
    user = data['user']
    for assignment in data['assignments']:
        task = Task.objects.create(
            runner=assignment.runner,
            status=Task.Status.QUEUED,
            push=push,
        )
        assignment_task = AssignmentTask.objects.create(
            user=user,
            assignment=assignment,
            task=task,
        )

        try:
            send_task(task)
        except:
            pass

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def github_webhook(request):
    if not 'X-GitHub-Delivery' in request.headers:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if not 'X-GitHub-Event' in request.headers:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if not 'X-Hub-Signature-256' in request.headers:
        return Response(status=status.HTTP_403_FORBIDDEN)
    signature_header = request.headers['X-Hub-Signature-256']
    secret_token = settings.GITHUB_WEBHOOK_TOKEN
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=request.body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        return Response(status=status.HTTP_403_FORBIDDEN)

    delivery = request.headers['X-GitHub-Delivery']
    event = request.headers['X-GitHub-Event']
    payload = json.loads(request.body)
    if event == 'push':
        push, created = Push.objects.get_or_create(
            delivery=delivery,
            defaults={'payload': payload},
        )
        if created:
            create_tasks(push)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_200_OK)
    elif event == 'organization':
        action = payload['action']
        if action == 'member_added':
            github_id = payload['membership']['user']['id']
            user = User.objects.get(social_auth__uid=github_id)
            from courses.models import Role # TODO
            for enrollment in user.enrollment_set.filter(role__kind=Role.Kind.STUDENT):
                role = enrollment.role
                offering_full_slug = role.offering.full_slug()
                repo_name = f'{offering_full_slug}-{user.username}'
                github_username = user.social_auth.get(provider='github').extra_data['login']
                from github_app.rest_api import GitHubRestAPI # TODO
                api = GitHubRestAPI()
                api.add_repository_collaborator_for_org(repo_name, github_username, permissions='push')

    return Response()
