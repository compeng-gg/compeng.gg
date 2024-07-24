from django.conf import settings
from social_django.utils import load_backend

from compeng_gg.auth.strategy import load_strategy, load_no_create_user_strategy

def auth_complete(provider, validated_data, user=None, allow_create_user=False):
    if allow_create_user:
        strategy = load_strategy(validated_data=validated_data)
    else:
        strategy = load_no_create_user_strategy(validated_data=validated_data)
    backend = load_backend(
        strategy=strategy,
        name=provider,
        redirect_uri=settings.AUTH_REDIRECT_URI,
    )
    return backend.auth_complete(user=user)

def disconnect(provider, user):
    strategy = load_no_create_user_strategy()
    backend = load_backend(
        strategy=strategy,
        name=provider,
        redirect_uri=None,
    )
    return backend.disconnect(user=user)
