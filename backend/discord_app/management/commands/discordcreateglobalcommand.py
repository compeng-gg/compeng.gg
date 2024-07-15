from django.core.management.base import BaseCommand, CommandError

from discord_app.rest_api import DiscordRestAPI

class Command(BaseCommand):

    help = 'Discord Create Global Command'

    def handle(self, *args, **options):
        data = {
            'name': 'anon',
            'type': DiscordRestAPI.COMMAND_TYPE_CHAT_INPUT,
            'description': 'Anonymize yourself',
            'options': [{
                'name': 'message',
                'type': DiscordRestAPI.COMMAND_OPTION_TYPE_STRING,
                'description': 'Send message anonymously',
                'required': True,
            }]
        }
        api = DiscordRestAPI()
        response = api.create_global_command_for_application(data)
        import json
        print(json.dumps(response, indent=4))
