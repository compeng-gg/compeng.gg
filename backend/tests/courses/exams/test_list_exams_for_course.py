from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_exam
from rest_framework import status
from datetime import timedelta


class ListExamsForCourse(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str) -> str:
        return f'/api/v0/exams/list/{course_slug}/'

    def test_happy_path(self):
        requesting_user_id = self.user.id

        now = timezone.now()

        exam_1_starts_at = now + timedelta(hours=1)
        exam_1 = create_exam(
            user_id=requesting_user_id,
            exam_title='final exam',
            course_slug='ece344',
            starts_at=exam_1_starts_at
        )
        exam_1.visible_at = now - timedelta(days=1)
        exam_1.save()

        exam_2_starts_at = now + timedelta(hours=2)
        exam_2 = create_exam(
            user_id=requesting_user_id,
            exam_title='ece454 midterm',
            course_slug='ece454',
            starts_at=exam_2_starts_at
        )
        exam_2.visible_at = now - timedelta(days=1)
        exam_2.save()

        response = self.client.get(self.get_api_endpoint('ece454'))

        expected_body = [
            {
                'title': 'ece454 midterm', 
                'start_unix_timestamp': int(exam_2.starts_at.timestamp()),
                'end_unix_timestamp': int(exam_2.ends_at.timestamp()),
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
