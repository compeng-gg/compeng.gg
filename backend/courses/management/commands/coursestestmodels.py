from django.core.management.base import BaseCommand, CommandError

from datetime import date

from courses.models import *

class Command(BaseCommand):
    help = "Populate Courses Test Models"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        uoft, _ = Institution.objects.get_or_create(
            slug='utoronto',
            defaults={
                'name': 'University of Toronto',
            }
        )
        ece344, _ = Course.objects.get_or_create(
            institution=uoft,
            slug='ece344',
            defaults={
                'name': 'ECE344',
                'title': 'Operating Systems',
            }
        )
        ece454, _ = Course.objects.get_or_create(
            institution=uoft,
            slug='ece454',
            defaults={
                'name': 'ECE454',
                'title': 'Computer Systems Programming',
            }
        )
        ece344_2024_fall, _ = Offering.objects.get_or_create(
            course=ece344,
            slug='2024-fall',
            defaults={
                'name': '2024 Fall',
                'start': date(2024, 9, 1),
                'end': date(2024, 12, 20),
                'active': True,
            }
        )
        ece454_2024_fall, _ = Offering.objects.get_or_create(
            course=ece454,
            slug='2024-fall',
            defaults={
                'name': '2024 Fall',
                'start': date(2024, 9, 1),
                'end': date(2024, 12, 20),
                'active': True,
            }
        )
