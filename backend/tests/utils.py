import courses.models as db
from datetime import (
    datetime,
    timedelta,
    timezone
)
from django.test import TestCase
import courses.models as db
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from uuid import UUID
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Optional


def create_offering(
    offering_name: str='fall 2024',
    course_name: str='ECE Capstone',
    course_slug: str='ECE496'
) -> db.Offering:
    intitution = db.Institution.objects.create()
    course = db.Course.objects.create(
        institution=intitution,
        name=course_name,
        slug=f'slug_{course_name}',
    )

    offering = db.Offering.objects.create(
        name=offering_name,
        course=course,
        start=timezone.now(),
        end=timezone.now() + timedelta(days=100),
        active=True
    )

    return offering

def create_offering_teams_settings(offering: db.Offering, max_team_size=3,formation_deadline=timezone.now()+timedelta(days=1)) -> db.OfferingTeamsSettings:
    return db.OfferingTeamsSettings.objects.create(
        offering=offering,
        max_team_size=max_team_size,
        formation_deadline=formation_deadline,
    )


def create_assessment(user_id: int) -> db.Assessment:
    offering = create_offering()
        
    student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

    db.Enrollment.objects.create(
        user_id=user_id,
        role=student_role,
    )

    start_datetime = datetime.now(timezone.utc)
    end_datetime = start_datetime + timedelta(hours=1)

    assessment = db.Assessment.objects.create(
        title='ECE454 Exam',
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        offering=offering,
    )
    
    return assessment


class TestCasesWithUserAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
