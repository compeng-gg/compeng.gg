from django.core.management.base import BaseCommand, CommandError

from discord.rest_api import DiscordRestAPI

class Command(BaseCommand):
    help = "GitHub Test"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Discord Test'))
        api = DiscordRestAPI()
        api.test()
