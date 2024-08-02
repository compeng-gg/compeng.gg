#this file contains logic to create  global commands (anon & undo) 
from django.core.management.base import BaseCommand, CommandError 
#BaseCommand:used to create custom management  commands
#CommandError is to handle errors during commands execution
from discord_app.rest_api import DiscordRestAPI
import json

class Command(BaseCommand):
    help = 'Create global Discord commands'

    def handle(self, *args, **options):
        api = DiscordRestAPI()

        # Define the "anon" command
        anon_command = {
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
        try:
            response = api.create_global_command_for_application(anon_command)
            self.stdout.write(self.style.SUCCESS('Anon command created:'))
            self.stdout.write(json.dumps(response, indent=4))
        except Exception as e:
            raise CommandError(f'Error occurred while creating anon command: {e}')

        # Define the "undo" command
        undo_command = {
            'name': 'undo',
            'type': DiscordRestAPI.COMMAND_TYPE_CHAT_INPUT,
            'description': 'Undo your last anonymous message',
        }
        try:
            response = api.create_global_command_for_application(undo_command)
            self.stdout.write(self.style.SUCCESS('Undo command created:'))
            #this line prints a success message to the console if the command is created successfully
            self.stdout.write(json.dumps(response, indent=4))
        except Exception as e: 
            raise CommandError(f'Error occurred while creating undo command: {e}')
