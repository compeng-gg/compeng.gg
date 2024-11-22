from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_assessment
from rest_framework import status
from django.contrib.auth.models import User
from datetime import timedelta


class ListAllAssessmentsTests(TestCasesWithUserAuth):
    API_ENDPOINT = '/api/v0/assessments/list/all/'

    def test_happy_path(self):
        requesting_user_id = self.user.id
        other_user_id = User.objects.create().id

        now = timezone.now()

        assessment_1_starts_at = now + timedelta(hours=1)
        assessment_1 = create_assessment(
            user_id=requesting_user_id,
            assessment_title='final exam',
            course_slug='ece344',
            starts_at=assessment_1_starts_at
        )
        assessment_1.visible_at = now - timedelta(days=1)
        assessment_1.save()

        assessment_2_starts_at = now + timedelta(hours=2)
        assessment_2 = create_assessment(
            user_id=requesting_user_id,
            assessment_title='midterm',
            course_slug='ece454',
            starts_at=assessment_2_starts_at
        )
        assessment_2.visible_at = now - timedelta(days=1)
        assessment_2.save()

        assessment_3_starts_at = now + timedelta(hours=2)
        assessment_3 = create_assessment(
            user_id=other_user_id,
            assessment_title='midterm',
            course_slug='aps105',
            starts_at=assessment_3_starts_at
        )
        assessment_3.visible_at = now - timedelta(days=1)
        assessment_3.save()

        response = self.client.get(self.API_ENDPOINT)

        expected_body = [
            {
                'title': 'final exam', 
                'start_unix_timestamp': int(assessment_1.starts_at.timestamp()),
                'end_unix_timestamp': int(assessment_1.ends_at.timestamp()),
                'course_slug': 'ece344'
            },
            {   
                'title': 'midterm',
                'start_unix_timestamp': int(assessment_2.starts_at.timestamp()),
                'end_unix_timestamp': int(assessment_2.ends_at.timestamp()),
                'course_slug': 'ece454'
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
