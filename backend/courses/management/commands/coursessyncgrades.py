from django.core.management.base import BaseCommand, CommandError

from courses.models import *
from courses.utils import get_grade_for_assignment

class Command(BaseCommand):
    help = "Populate Courses Grades"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for offering in Offering.objects.all():
            self.stdout.write(
                self.style.SUCCESS(f'Syncing {offering}')
            )
            student_role = Role.objects.get(kind=Role.Kind.STUDENT, offering=offering)
            for assignment in offering.assignment_set.all():
                for enrollment in Enrollment.objects.filter(role=student_role):
                    user = enrollment.user
                    grade = get_grade_for_assignment(user, assignment)
