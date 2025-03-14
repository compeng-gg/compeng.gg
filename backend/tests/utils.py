import courses.models as db
from datetime import datetime, timedelta, timezone
from django.utils import timezone
from django.utils.text import slugify
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Optional
from django.contrib.contenttypes.models import ContentType
from enum import IntEnum

class Kind(IntEnum):
    INSTRUCTOR = 1
    TA = 2
    STUDENT = 3
    AUDIT = 4

def create_student_role(offering: db.Offering):
    return create_role(Kind.STUDENT, offering)

def create_role(
    kind: Kind,
    offering: db.Offering,
    ) -> db.Role:
    role = db.Role.objects.create(
        kind=kind,
        offering=offering 
    )
    return role

def create_offering(
    offering_name: str = "fall 2024",
    course_name: str = "ECE Capstone",
    course_slug: str = "ECE496",
) -> db.Offering:
    intitution = db.Institution.objects.create()
    course = db.Course.objects.create(
        institution=intitution, name=course_name, slug=course_slug
    )

    offering = db.Offering.objects.create(
        name=offering_name,
        slug=slugify(offering_name),
        course=course,
        start=timezone.now(),
        end=timezone.now() + timedelta(days=100),
        active=True,
    )

    return offering


def create_offering_teams_settings(
    offering: db.Offering,
    max_team_size=3,
    formation_deadline=timezone.now() + timedelta(days=1),
) -> db.OfferingTeamsSettings:
    return db.OfferingTeamsSettings.objects.create(
        offering=offering,
        max_team_size=max_team_size,
        formation_deadline=formation_deadline,
    )


def create_repository(
    id: Optional[int] = 1,
    name: Optional[str] = "reimagined-parakeet",
    full_name: Optional[str] = "nickwood5/reimagined-parakeet",
) -> db.Repository:
    mock_content_type, _ = ContentType.objects.get_or_create(
        app_label="your_app", model="mock_model"
    )

    mock_repository = db.Repository.objects.create(
        id=id,
        name=name,
        full_name=full_name,
        owner_content_type=mock_content_type,
        owner_id=1,
    )

    return mock_repository

def create_student_enrollment(
    user_id: int, offering: db.Offering
) -> db.Enrollment:
    return create_enrollment(user_id, offering, Kind.STUDENT)

def create_enrollment(
    user_id: int, offering: db.Offering, kind: db.Role.Kind
) -> db.Enrollment:
    role, _ = db.Role.objects.get_or_create(kind=kind, offering=offering)

    return db.Enrollment.objects.create(
        user_id=user_id,
        role=role,
    )


def create_quiz(
    user_id: Optional[int]=None,
    quiz_title: Optional[str] = "Final Quiz",
    course_slug: Optional[str] = "ECE454",
    visible_at: Optional[datetime] = timezone.now(),
    starts_at: Optional[datetime] = timezone.now(),
    ends_at: Optional[datetime] = timezone.now() + timedelta(hours=1),
    content_viewable_after_submission: Optional[bool] = True,
    repository_id: Optional[int] = 1,
    repository_name: Optional[str] = "repo_name",
    repository_full_name: Optional[str] = "user/repo_name",
    offering: Optional[db.Offering]=None,
    quiz_slug: Optional[str]="quiz_slug"
) -> db.Quiz:
    if offering is None:
        offering = create_offering(course_slug=course_slug)

    if user_id is not None:
        create_enrollment(user_id, offering, db.Role.Kind.STUDENT)

    ends_at = starts_at + timedelta(hours=1)
    visible_at = starts_at - timedelta(hours=1)

    repository = create_repository(
        id=repository_id, name=repository_name, full_name=repository_full_name
    )

    quiz = db.Quiz.objects.create(
        title=quiz_title,
        starts_at=starts_at,
        slug=quiz_slug,
        ends_at=ends_at,
        visible_at=visible_at,
        offering=offering,
        content_viewable_after_submission=content_viewable_after_submission,
        repository=repository,
    )

    return quiz


def create_quiz_submission(
        user_id: int, 
        quiz: db.Quiz,
    ) -> db.QuizSubmission:
    started_at = timezone.now()
    return db.QuizSubmission.objects.create(
        user_id=user_id,
        quiz=quiz,
        started_at=started_at,
        completed_at=started_at + timedelta(minutes=30),
    )


def create_coding_question(
    quiz: db.Quiz,
    prompt: Optional[str] = "Prompt for a coding question",
    order: Optional[int] = 0,
    points: Optional[int] = 20,
    programming_lanaguage: Optional[
        db.CodingQuestion.ProgrammingLanguage
    ] = db.CodingQuestion.ProgrammingLanguage.PYTHON,
    files: Optional[list[str]] = ["test.py"],
):
    return db.CodingQuestion.objects.create(
        quiz=quiz,
        prompt=prompt,
        order=order,
        points=points,
        programming_language=programming_lanaguage,
        files=files,
    )


def create_checkbox_question(
    quiz: db.Quiz,
    prompt: Optional[str] = "Prompt for a coding question",
    order: Optional[int] = 0,
    points: Optional[int] = 20,
    options: Optional[list[str]] = ["Option 1", "Option 2"],
    correct_option_indices: Optional[list[str]] = [0],
):
    return db.CheckboxQuestion.objects.create(
        quiz=quiz,
        prompt=prompt,
        order=order,
        points=points,
        options=options,
        correct_option_indices=correct_option_indices,
    )


def create_multiple_choice_question(
    quiz: db.Quiz,
    prompt: Optional[str] = "Prompt for a multiple choice question",
    order: Optional[int] = 0,
    points: Optional[int] = 20,
    options: Optional[list[str]] = ["Option 1", "Option 2"],
    correct_option_index: Optional[int] = 0,
):
    return db.MultipleChoiceQuestion.objects.create(
        quiz=quiz,
        prompt=prompt,
        order=order,
        points=points,
        options=options,
        correct_option_index=correct_option_index,
    )


def create_written_response_question(
    quiz: db.Quiz,
    prompt: Optional[str] = "Prompt for a written response question",
    order: Optional[int] = 0,
    points: Optional[int] = 20,
    max_length: Optional[int] = 500,
):
    return db.WrittenResponseQuestion.objects.create(
        quiz=quiz,
        prompt=prompt,
        order=order,
        points=points,
        max_length=max_length,
    )

def create_user(username):
    return User.objects.create_user(
            username=username, password="testpassword"
        )

def create_quiz_accommodation(
    user: User, 
    quiz: db.Quiz,
    visible_at: Optional[datetime]=timezone.now(),
    starts_at: Optional[datetime]=timezone.now() + timedelta(days=1),
    ends_at: Optional[datetime]=timezone.now() + timedelta(days=1, hours=1),
):
    return db.QuizAccommodation.objects.create(
        user=user,
        quiz=quiz,
        starts_at=starts_at,
        ends_at=ends_at,
        visible_at=visible_at
    )

class TestCasesWithUserAuth(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
