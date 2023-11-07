from social_core.exceptions import AuthForbidden

def disallow_new_discord(backend, is_new, *args, **kwargs):
    if backend.name == 'discord' and is_new:
        raise AuthForbidden(backend)
