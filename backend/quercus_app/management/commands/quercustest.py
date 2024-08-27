from django.core.management.base import BaseCommand, CommandError

from quercus_app.utils import update_courses_from_quercus

class Command(BaseCommand):
    help = "Quercus Test"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Quercus Test'))
        update_courses_from_quercus()
