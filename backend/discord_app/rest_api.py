from compeng_gg.rest_api import RestAPI

from django.conf import settings

import logging
import json
import requests

logger = logging.getLogger(__name__)

class DiscordRestAPI(RestAPI):

    API_URL = 'https://discord.com/api/v10'
    APPLICATION_ID = settings.SOCIAL_AUTH_DISCORD_KEY
    BOT_TOKEN = settings.DISCORD_BOT_TOKEN
    GUILD_ID = settings.DISCORD_GUILD_ID

    COLOR_BLUE    = 0x007FA3
    COLOR_CYAN    = 0x00A189
    COLOR_GREEN   = 0x8DBF2E
    COLOR_MAGENTA = 0xAB1368
    COLOR_PURPLE  = 0x9E34B0
    COLOR_RED     = 0xDC4633
    COLOR_YELLOW  = 0xF1C500

    COMMAND_TYPE_CHAT_INPUT = 1

    COMMAND_OPTION_TYPE_SUB_COMMAND       = 1
    COMMAND_OPTION_TYPE_SUB_COMMAND_GROUP = 2
    COMMAND_OPTION_TYPE_STRING            = 3

    CHANNEL_TYPE_GUILD_TEXT          =  0
    CHANNEL_TYPE_DM                  =  1
    CHANNEL_TYPE_GUILD_VOICE         =  2
    CHANNEL_TYPE_GROUP_DM            =  3
    CHANNEL_TYPE_GUILD_CATEGORY      =  4
    CHANNEL_TYPE_GUILD_ANNOUNCEMENT  =  5
    CHANNEL_TYPE_ANNOUNCEMENT_THREAD = 10
    CHANNEL_TYPE_PUBLIC_THREAD       = 11
    CHANNEL_TYPE_PRIVATE_THREAD      = 12
    CHANNEL_TYPE_GUILD_STAGE_VOICE   = 13
    CHANNEL_TYPE_GUILD_DIRECTORY     = 14
    CHANNEL_TYPE_GUILD_FORUM         = 15
    CHANNEL_TYPE_GUILD_MEDIA         = 16

    PERMISSION_VIEW_CHANNEL = 0x400

    def __init__(self):
        super().__init__()

    def delete(self, endpoint):
        token = self.BOT_TOKEN
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bot {token}',
        }
        r = requests.delete(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        return r.json()

    def get(self, endpoint):
        token = self.BOT_TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bot {token}',
        }
        r = requests.get(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def patch(self, endpoint, data=None):
        token = self.BOT_TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bot {token}',
        }
        if data is not None:
            r = requests.patch(
                f'{self.API_URL}{endpoint}',
                headers=headers,
                json=data,
            )
        else:
            r = requests.put(
                f'{self.API_URL}{endpoint}',
                headers=headers,
            )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def post(self, endpoint, data=None):
        token = self.BOT_TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bot {token}',
        }
        if data is not None:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
                json=data,
            )
        else:
            r = requests.post(
                f'{self.API_URL}{endpoint}',
                headers=headers,
            )
        r.raise_for_status()
        return r.json()

    def put(self, endpoint, data=None):
        token = self.BOT_TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bot {token}',
        }
        if data is not None:
            r = requests.put(
                f'{self.API_URL}{endpoint}',
                headers=headers,
                json=data,
            )
        else:
            r = requests.put(
                f'{self.API_URL}{endpoint}',
                headers=headers,
            )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def get_guild_channels(self, guild_id):
        return self.get(f'/guilds/{guild_id}/channels')

    def get_guild_channels_for_guild(self):
        return self.get_guild_channels(self.GUILD_ID)

    # Requires `CREATE_INSTANT_INVITE` permission
    def add_guild_member(self, guild_id, user_id, access_token, **kwargs):
        kwargs['access_token'] = access_token
        return self.put(f'/guilds/{guild_id}/members/{user_id}', kwargs)

    def add_guild_member_for_guild(self, user_id, access_token, **kwargs):
        return self.add_guild_member(
            self.GUILD_ID, user_id, access_token, **kwargs
        )

    # Requires `MANAGE_CHANNELS` permission
    def create_guild_channel(self, guild_id, name, **kwargs):
        kwargs['name'] = name
        return self.post(f'/guilds/{guild_id}/channels', kwargs)

    def create_guild_channel_for_guild(self, name, **kwargs):
        return self.create_guild_channel(self.GUILD_ID, name, **kwargs)

    # Requires `MANAGE_ROLES` permission
    def get_guild_roles(self, guild_id):
        return self.get(f'/guilds/{guild_id}/roles')

    def get_guild_roles_for_guild(self):
        return self.get_guild_roles(self.GUILD_ID)

    # Requires `MANAGE_ROLES` permission
    def modify_guild_role(self, guild_id, role_id, **kwargs):
        return self.patch(f'/guilds/{guild_id}/roles/{role_id}', kwargs)

    def modify_guild_role_for_guild(self, role_id, **kwargs):
        return self.modify_guild_role(self.GUILD_ID, role_id, **kwargs)

    # Requires `MANAGE_ROLES` permission
    def create_guild_role(self, guild_id, name, color, **kwargs):
        kwargs['name'] = name
        kwargs['color'] = color
        return self.post(f'/guilds/{guild_id}/roles', kwargs)

    def create_guild_role_for_guild(self, name, color, **kwargs):
        return self.create_guild_role(self.GUILD_ID, name, color, **kwargs)

    def add_guild_member_role(self, guild_id, user_id, role_id):
        return self.put(f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def add_guild_member_role_for_guild(self, user_id, role_id):
        return self.add_guild_member_role(self.GUILD_ID, user_id, role_id)

    def remove_guild_member_role(self, guild_id, user_id, role_id):
        return self.delete(f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def remove_guild_member_role_for_guild(self, user_id, role_id):
        return self.remove_guild_member_role(self.GUILD_ID, user_id, role_id)

    def get_global_commands(self, application_id):
        return self.get(f'/applications/{application_id}/commands')

    def get_global_commands_for_application(self):
        return self.get_global_commands(self.APPLICATION_ID)

    def create_global_command(self, application_id, data):
        return self.post(f'/applications/{application_id}/commands', data)

    def create_global_command_for_application(self, data):
        return self.create_global_command(self.APPLICATION_ID, data)

    def delete_global_command(self, application_id, command_id):
        return self.delete(
            f'/applications/{application_id}/commands/{command_id}'
        )

    def delete_global_command_for_application(self, command_id):
        return self.delete_global_command(self.APPLICATION_ID, command_id)

    def get_current_user(self):
        return self.get('/users/@me')

    def test(self):
        #print(json.dumps(self.get_guild_roles_for_guild(), indent=4))
        #print(json.dumps(self.create_command_for_application(), indent=4))
        #print(json.dumps(self.get_global_commands_for_application(), indent=4))
        #print(json.dumps(self.get_current_user(), indent=4))

        # print(json.dumps(self.create_guild_channel_for_guild('Test', type=self.CHANNEL_TYPE_GUILD_CATEGORY), indent=4))
        print(json.dumps(self.get_guild_channels_for_guild(), indent=4))

        #from django.contrib.auth.models import User
        #from courses.models import Role
        #from social_django.utils import load_strategy
        #user = User.objects.get(username='jon')
        #role = Role.objects.get(offering__course__slug='ece454', kind=Role.Kind.INSTRUCTOR)

        #social = user.social_auth.get(provider='discord')
        #strategy = load_strategy()
        #access_token = social.get_access_token(strategy)
        #user_id = social.uid
        #self.add_guild_member_role_for_guild(user_id, role.discord_role_id)

        # print(user_id, role.discord_role_id)
        #print(self.create_guild_role_for_guild('test'))
