import hashlib
import hmac

from compeng_gg.django.github.utils import get_or_create_delivery
from compeng_gg.django.github.rest_framework.serializers import DeliverySerializer
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from urllib.parse import unquote_to_bytes

@api_view(["GET", "POST"])
@parser_classes([FormParser, JSONParser])
@permission_classes([AllowAny])
def webhook(request):
    required_headers = [
        "X-GitHub-Delivery",
        "X-GitHub-Event",
        "X-Hub-Signature-256",
        "X-GitHub-Hook-ID",
    ]
    for header in required_headers:
        if not header in request.headers:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # Digest the raw bytes for the data 
    secret = settings.GITHUB_WEBHOOK_SECRET.encode()
    digest_maker = hmac.new(secret, digestmod=hashlib.sha256)
    if request.content_type == "application/json":
        digest_maker.update(request.body)
    elif request.method == "GET":
        digest_maker.update(request.query_params["payload"].encode())
    elif request.content_type == "application/x-www-form-urlencoded":
        payload_bytes = request.body[len(b"payload="):]
        payload_bytes = payload_bytes.replace(b"+", b" ")
        payload_bytes = unquote_to_bytes(payload_bytes)
        digest_maker.update(payload_bytes)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Check the signature
    signature = request.headers["X-Hub-Signature-256"]
    digest = digest_maker.hexdigest()
    if not hmac.compare_digest(signature, f"sha256={digest}"):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.content_type == "application/json":
        validated_data = {"payload": request.data}
    else:
        if request.method == "GET":
            data = request.query_params
        elif request.content_type == "application/x-www-form-urlencoded":
            data = request.data
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = DeliverySerializer(data=data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data

    hook_id = request.headers["X-GitHub-Hook-ID"]
    delivery_uuid = request.headers["X-GitHub-Delivery"]
    event = request.headers["X-GitHub-Event"]
    payload = validated_data["payload"]

    try:
        get_or_create_delivery(hook_id, delivery_uuid, event, payload)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)
