from django.core.management.base import BaseCommand, CommandError

from github_app.utils import create_fork
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "GitHub Test"

    def add_arguments(self, parser):
        parser.add_argument('course_slug')

    def handle(self, *args, **options):
        course_slug = options['course_slug']
        self.stdout.write(self.style.SUCCESS(f'Creating {course_slug} forks...'))
        for user in User.objects.all():
            create_fork(course_slug, user)

