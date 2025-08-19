from django.core.management.base import BaseCommand, CommandError

from courses.models import *
from api.v0.views import _get_assignment_data

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("course_slug")
        parser.add_argument("assignment_slug")

    def handle(self, *args, **options):
        offering = Offering.objects.get(
            course__slug=options["course_slug"],
            active=True
        )
        role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)
        assignment = Assignment.objects.get(offering=offering, slug=options["assignment_slug"])

        self.stdout.write("utorid,grade")
        for enrollment in Enrollment.objects.filter(role=role).order_by('user__username'):
            user = enrollment.user
            assignment_data = _get_assignment_data(assignment, user)
            grade = assignment_data["raw_grade"]
            self.stdout.write(f"{user.username},{grade}")

