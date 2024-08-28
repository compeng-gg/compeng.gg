from django.core.management.base import BaseCommand, CommandError

from courses.models import Enrollment
from compeng_gg.auth import get_uid
from github_app.utils import add_github_team_membership_for_enrollment

class Command(BaseCommand):
    help = "GitHub Test"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('GitHub Test'))
        for enrollment in Enrollment.objects.all():
            user = enrollment.user
            try:
                get_uid('github', user)
            except:
                continue
            add_github_team_membership_for_enrollment(enrollment)
