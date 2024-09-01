from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import hashlib
import hmac
import json

from django.conf import settings
from github_app.models import Push


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def github_webhook(request):
    if not 'X-Hub-Signature-256' in request.headers:
        return Response(status=status.HTTP_403_FORBIDDEN)
    signature_header = request.headers['X-Hub-Signature-256']
    secret_token = settings.GITHUB_WEBHOOK_TOKEN
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=request.body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    print(expected_signature)
    if not hmac.compare_digest(expected_signature, signature_header):
        return Response(status=status.HTTP_403_FORBIDDEN)

    Push.objects.create(payload=json.loads(request.body))
    return Response()
