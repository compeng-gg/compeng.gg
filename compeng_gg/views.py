from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from social_django.utils import load_strategy

@login_required
def login_redirect(request):
    return HttpResponseRedirect(
        reverse('profile', args=[request.user.username])
    )

def profile(request, username):
    if not request.user.is_authenticated:
        raise Http404("Not authenticated")
    if not request.user.username == username:
        raise Http404("User not found")

    try:
        social = request.user.social_auth.get(provider='laforge')
        strategy = load_strategy(request)
        backend = social.get_backend_instance(strategy)
        access_token = social.get_access_token(strategy)
        laforge_data = backend.user_data(access_token)
    except:
        laforge_data = None

    try:
        social = request.user.social_auth.get(provider='discord')
        strategy = load_strategy(request)
        backend = social.get_backend_instance(strategy)
        access_token = social.get_access_token(strategy)
        discord_data = backend.user_data(access_token)
    except:
        discord_data = None

    return render(request, 'profile.html', {
        'username': username,
        'laforge_data': laforge_data,
        'discord_data': discord_data,
    })
