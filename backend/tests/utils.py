import courses.models as db
from datetime import (
    datetime,
    timedelta,
    timezone
)
from django.utils import timezone
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
        slug=course_slug
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


def create_quiz(
    user_id: int,
    quiz_title: Optional[str]='Final Quiz',
    course_slug: Optional[str]='ECE454',
    starts_at: Optional[datetime]=timezone.now(),
    content_viewable_after_submission: Optional[bool]=True
) -> db.Quiz:
    offering = create_offering(course_slug=course_slug)
        
    student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

    db.Enrollment.objects.create(
        user_id=user_id,
        role=student_role,
    )

    ends_at = starts_at + timedelta(hours=1)
    visible_at = starts_at - timedelta(hours=1)

    quiz = db.Quiz.objects.create(
        title=quiz_title,
        starts_at=starts_at,
        slug="slug",
        ends_at=ends_at,
        visible_at=visible_at,
        offering=offering,
        content_viewable_after_submission=content_viewable_after_submission
    )
    
    return quiz


def create_quiz_submission(user_id: int, course_slug: str, quiz_slug: str) -> db.QuizSubmission:
    started_at = timezone.now()
    return db.QuizSubmission.objects.create(
        user_id=user_id,
        quiz_slug=quiz_slug,
        started_at=started_at,
        completed_at=started_at + timedelta(hours=1)
    )


class TestCasesWithUserAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
