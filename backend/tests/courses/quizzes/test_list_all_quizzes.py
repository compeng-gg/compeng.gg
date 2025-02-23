from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_quiz
from rest_framework import status
from django.contrib.auth.models import User
from datetime import timedelta


class ListAllQuizzesTests(TestCasesWithUserAuth):
    API_ENDPOINT = "/api/v0/quizzes/list/all/"

    def test_happy_path(self):
        requesting_user_id = self.user.id
        other_user_id = User.objects.create().id

        now = timezone.now()

        quiz_1_starts_at = now + timedelta(hours=1)
        quiz_1 = create_quiz(
            user_id=requesting_user_id,
            quiz_title="final quiz",
            course_slug="ece344",
            starts_at=quiz_1_starts_at,
            repository_id=1,
            repository_full_name="user/repo_1",
        )
        quiz_1.visible_at = now - timedelta(days=1)
        quiz_1.save()

        quiz_2_starts_at = now + timedelta(hours=2)
        quiz_2 = create_quiz(
            user_id=requesting_user_id,
            quiz_title="midterm",
            course_slug="ece454",
            starts_at=quiz_2_starts_at,
            repository_id=2,
            repository_full_name="user/repo_2",
        )
        quiz_2.visible_at = now - timedelta(days=1)
        quiz_2.save()

        quiz_3_starts_at = now + timedelta(hours=2)
        quiz_3 = create_quiz(
            user_id=other_user_id,
            quiz_title="midterm",
            course_slug="aps105",
            starts_at=quiz_3_starts_at,
            repository_id=3,
            repository_full_name="user/repo_3",
        )
        quiz_3.visible_at = now - timedelta(days=1)
        quiz_3.save()

        response = self.client.get(self.API_ENDPOINT)

        expected_body = [
            {
                "title": "final quiz",
                "start_unix_timestamp": int(quiz_1.starts_at.timestamp()),
                "end_unix_timestamp": int(quiz_1.ends_at.timestamp()),
                "course_slug": "ece344",
                "slug": quiz_1.slug,
            },
            {
                "title": "midterm",
                "start_unix_timestamp": int(quiz_2.starts_at.timestamp()),
                "end_unix_timestamp": int(quiz_2.ends_at.timestamp()),
                "course_slug": "ece454",
                "slug": quiz_2.slug,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
