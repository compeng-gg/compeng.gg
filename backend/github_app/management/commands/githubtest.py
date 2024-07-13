from django.core.management.base import BaseCommand, CommandError

from github_app.rest_api import GitHubRestAPI

class Command(BaseCommand):
    help = "GitHub Test"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        api = GitHubRestAPI()
        self.stdout.write(self.style.SUCCESS('Test'))
        api.test()
