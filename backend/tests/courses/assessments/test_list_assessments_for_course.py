from tests.utils import TestCasesWithUserAuth
from django.utils import timezone
from tests.utils import create_assessment
from rest_framework import status
from datetime import timedelta


class ListAssessmentsForCourse(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str) -> str:
        return f'/api/v0/assessments/list/{course_slug}/'

    def test_happy_path(self):
        requesting_user_id = self.user.id

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
            assessment_title='ece454 midterm',
            course_slug='ece454',
            starts_at=assessment_2_starts_at
        )
        assessment_2.visible_at = now - timedelta(days=1)
        assessment_2.save()

        response = self.client.get(self.get_api_endpoint('ece454'))

        expected_body = [
            {
                'title': 'ece454 midterm', 
                'start_unix_timestamp': int(assessment_2.starts_at.timestamp()),
                'end_unix_timestamp': int(assessment_2.ends_at.timestamp()),
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_body)
