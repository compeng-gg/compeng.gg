from django.contrib.auth.models import User

def associate_by_username(backend, details, user=None, *args, **kwargs):
    if user:
        return None
    
    if backend.name != 'laforge':
        return None

    username = details.get('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None

    if user.email == '':
        user.email = details.get('email')
        user.save()
    return {"user": user, "is_new": False}
