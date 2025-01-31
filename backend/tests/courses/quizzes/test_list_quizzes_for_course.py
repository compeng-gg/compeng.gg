from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_quiz
from rest_framework import status
from datetime import timedelta


class ListQuizzesForCourse(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str) -> str:
        return f'/api/v0/quizzes/list/{course_slug}/'

    def test_happy_path(self):
        requesting_user_id = self.user.id

        now = timezone.now()

        quiz_1_starts_at = now + timedelta(hours=1)
        quiz_1 = create_quiz(
            user_id=requesting_user_id,
            quiz_title='final quiz',
            course_slug='ece344',
            starts_at=quiz_1_starts_at,
            repository_id=1,
            repository_full_name="user/repo_1"
        )
        quiz_1.visible_at = now - timedelta(days=1)
        quiz_1.save()

        quiz_2_starts_at = now + timedelta(hours=2)
        quiz_2 = create_quiz(
            user_id=requesting_user_id,
            quiz_title='ece454 midterm',
            course_slug='ece454',
            starts_at=quiz_2_starts_at,
            repository_id=2,
            repository_full_name="user/repo_2"
        )
        quiz_2.visible_at = now - timedelta(days=1)
        quiz_2.save()

        response = self.client.get(self.get_api_endpoint('ece454'))

        expected_body = [
            {
                'title': 'ece454 midterm', 
                'start_unix_timestamp': int(quiz_2.starts_at.timestamp()),
                'end_unix_timestamp': int(quiz_2.ends_at.timestamp()),
                'slug': quiz_2.slug
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
