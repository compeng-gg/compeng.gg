from django.core.management.base import BaseCommand, CommandError

from courses.models import *

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("course_slug")

    def handle(self, *args, **options):
        offering = Offering.objects.get(
            course__slug=options["course_slug"],
            active=True
        )
        role = Role.objects.get(offering=offering, kind=Role.Kind.STUDENT)

        institution = Institution.objects.get(slug="utoronto")

        self.stdout.write("utorid,student_id,first_name,last_name")
        for enrollment in Enrollment.objects.filter(role=role).order_by('user__username'):
            user = enrollment.user
            student_id = ""
            try:
                member = Member.objects.get(institution=institution, user=user)
                student_id = member.external_id
            except Member.DoesNotExist:
                pass
            self.stdout.write(f"{user.username},{student_id},{user.first_name},{user.last_name}")

