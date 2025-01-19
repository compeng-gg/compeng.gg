from django.core.management.base import BaseCommand, CommandError

from courses.models import *
from courses.utils import populate_assignment_grades

class Command(BaseCommand):
    help = "Fix Private Grades"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for offering in Offering.objects.filter(active=True):
            self.stdout.write(
                self.style.SUCCESS(f'Syncing {offering}')
            )
            for assignment in offering.assignment_set.all():
                for enrollment in Enrollment.objects.filter(role__offering=offering):
                    user = enrollment.user
                    for assignment_task in AssignmentTask.objects.filter(user=user, assignment=assignment):
                        populate_assignment_grades(assignment_task.task)
