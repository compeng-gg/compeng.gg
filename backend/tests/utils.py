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
from django.contrib.contenttypes.models import ContentType


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

def create_repository(
    id: Optional[int]=1,
    name: Optional[str]="reimagined-parakeet",
    full_name: Optional[str]="nickwood5/reimagined-parakeet"
) -> db.Repository:
    mock_content_type, _ = ContentType.objects.get_or_create(app_label="your_app", model="mock_model")

    mock_repository = db.Repository.objects.create(
        id=id,
        name=name,
        full_name=full_name,
        owner_content_type=mock_content_type,
        owner_id=1,
    )

    return mock_repository

def create_student_enrollment(
    user_id: int,
    offering: db.Offering
) -> db.Enrollment:
    student_role, _ = db.Role.objects.get_or_create(kind=db.Role.Kind.STUDENT, offering=offering)

    return db.Enrollment.objects.create(
        user_id=user_id,
        role=student_role,
    )

def create_quiz(
    user_id: int,
    quiz_title: Optional[str]='Final Quiz',
    course_slug: Optional[str]='ECE454',
    starts_at: Optional[datetime]=timezone.now(),
    content_viewable_after_submission: Optional[bool]=True,
    repository_id: Optional[int]=1,
    repository_name: Optional[str]="repo_name",
    repository_full_name: Optional[str]="user/repo_name"
) -> db.Quiz:
    offering = create_offering(course_slug=course_slug)

    create_student_enrollment(user_id, offering)

    ends_at = starts_at + timedelta(hours=1)
    visible_at = starts_at - timedelta(hours=1)

    repository = create_repository(
        id=repository_id,
        name=repository_name,
        full_name=repository_full_name
    )

    quiz = db.Quiz.objects.create(
        title=quiz_title,
        starts_at=starts_at,
        slug="quiz_slug",
        ends_at=ends_at,
        visible_at=visible_at,
        offering=offering,
        content_viewable_after_submission=content_viewable_after_submission,
        repository=repository
    )
    
    return quiz


def create_quiz_submission(
        user_id: int,
        quiz: db.Quiz
    ) -> db.QuizSubmission:
    started_at = timezone.now()
    return db.QuizSubmission.objects.create(
        user_id=user_id,
        quiz=quiz,
        started_at=started_at,
        completed_at=started_at + timedelta(hours=1)
    )

def create_coding_question(
    quiz: db.Quiz,
    prompt: Optional[str]="Prompt for a coding question",
    order: Optional[int]=0,
    points: Optional[int]=20,
    programming_lanaguage: Optional[db.CodingQuestion.ProgrammingLanguage]=db.CodingQuestion.ProgrammingLanguage.PYTHON,
    files: Optional[list[str]]=['test.py']
):
    return db.CodingQuestion.objects.create(
        quiz=quiz,
        prompt=prompt,
        order=order,
        points=points,
        programming_language=programming_lanaguage,
        files=files
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
