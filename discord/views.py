from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from social_django.utils import load_strategy

import requests

API_ENDPOINT = 'https://discord.com/api/v10'
GUILD_ID = '919041347674066995'
VERIFIED_ROLE_ID = '1136004776425963561'
APS_105_STUDENT_ROLE_ID = '1191861499233320970'
ECE_353_STUDENT_ROLE_ID = '1191867273523253278'

def add_discord_guild_member(user_id, access_token, role_id):
    roles = [VERIFIED_ROLE_ID, role_id]
    url = f"{API_ENDPOINT}/guilds/{GUILD_ID}/members/{user_id}"
    data = {
        'access_token': access_token,
        'roles': roles,
    }
    headers = {
        'Authorization': f"Bot {settings.DISCORD_BOT_TOKEN}",
    }
    r = requests.put(url, json=data, headers=headers)
    if r.status_code == 204:
        return {}
    r.raise_for_status()
    return r.json()

def add_discord_guild_roles(user_id, roles):
    for role_id in roles:
        url = f"{API_ENDPOINT}/guilds/{GUILD_ID}/members/{user_id}/roles/{role_id}"
        headers = {
            'Authorization': f"Bot {settings.DISCORD_BOT_TOKEN}",
        }
        requests.put(url, headers=headers)

@login_required(login_url='/auth/login/laforge/')
def join(request, role):
    user = request.user
    try:
        social = user.social_auth.get(provider='discord')
    except ObjectDoesNotExist:
        # TODO: This could be a real error if the account is already associated
        #       with a different user account.
        return redirect(f'/auth/login/discord/?next={request.path}')

    strategy = load_strategy(request)
    access_token = social.get_access_token(strategy)
    user_id = social.uid

    role_id = None
    if role == 'aps105':
        role_id = APS_105_STUDENT_ROLE_ID
    elif role == 'ece353':
        role_id = ECE_353_STUDENT_ROLE_ID
    
    if role_id is not None:
        data = add_discord_guild_member(user_id, access_token, role_id)
        if not data:
            add_discord_guild_roles(user_id, [VERIFIED_ROLE_ID, role_id])
    
    return redirect('profile', request.user.username)