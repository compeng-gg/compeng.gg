from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_exam
from rest_framework import status
from django.contrib.auth.models import User
from datetime import timedelta


class ListAllExamsTests(TestCasesWithUserAuth):
    API_ENDPOINT = '/api/v0/exams/list/all/'

    def test_happy_path(self):
        requesting_user_id = self.user.id
        other_user_id = User.objects.create().id

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
            exam_title='midterm',
            course_slug='ece454',
            starts_at=exam_2_starts_at
        )
        exam_2.visible_at = now - timedelta(days=1)
        exam_2.save()

        exam_3_starts_at = now + timedelta(hours=2)
        exam_3 = create_exam(
            user_id=other_user_id,
            exam_title='midterm',
            course_slug='aps105',
            starts_at=exam_3_starts_at
        )
        exam_3.visible_at = now - timedelta(days=1)
        exam_3.save()

        response = self.client.get(self.API_ENDPOINT)

        expected_body = [
            {
                'title': 'final exam', 
                'start_unix_timestamp': int(exam_1.starts_at.timestamp()),
                'end_unix_timestamp': int(exam_1.ends_at.timestamp()),
                'course_slug': 'ece344'
            },
            {   
                'title': 'midterm',
                'start_unix_timestamp': int(exam_2.starts_at.timestamp()),
                'end_unix_timestamp': int(exam_2.ends_at.timestamp()),
                'course_slug': 'ece454'
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
