"""
ASGI config for compeng_gg project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compeng_gg.settings')

asgi_application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from api.v0.websocket_urls import websocket_urlpatterns
from django.contrib.auth.models import (
    AnonymousUser,
    User
)


@database_sync_to_async
def get_user_from_token(token):
    try:
        valid_data = UntypedToken(token)
        return User.objects.get(id=valid_data['user_id'])
    except Exception:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware for WebSocket token authentication.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = dict(pair.split('=') for pair in query_string.split('&') if '=' in pair)

        token = params.get('token')

        if token is None:
            raise Exception()

        scope['user'] = await get_user_from_token(token)
 
        return await self.inner(scope, receive, send)


application = ProtocolTypeRouter({
    'http': asgi_application,
    'websocket': TokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns,  # Add the prefix here
        )
    ),
})
