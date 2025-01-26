from django.core.management.base import BaseCommand, CommandError

from courses.models import *
from quercus_app.utils import sync_assignment_to_quercus

class Command(BaseCommand):
    help = "Add Quercus Assignments"

    def add_arguments(self, parser):
        parser.add_argument("course_slug", type=str)
        parser.add_argument("assignment_slugs", nargs="+", type=str)

    def handle(self, *args, **options):

        offering = Offering.objects.get(active=True, course__slug=options["course_slug"])
        for assignment_slug in options["assignment_slugs"]:
            assignment = offering.assignment_set.get(slug=assignment_slug)
            sync_assignment_to_quercus(assignment)
