import subprocess

from compeng_gg.django.github.models import Push
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("push_id", type=int)

    def handle(self, *args, **options):
        push_id = options["push_id"]
        try:
            push = Push.objects.get(id=push_id)
        except Push.DoesNotExist:
            raise CommandError(f'Push {push_id} does not exist')

        print("Got", push_id)
