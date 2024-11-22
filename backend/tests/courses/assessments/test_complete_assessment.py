from tests.utils import TestCasesWithUserAuth
import courses.models as db
from django.utils import timezone
from tests.utils import (
    create_assessment,
    create_assessment_submission
)
from rest_framework import status
from uuid import (
    uuid4,
    UUID
)


class CompleteAssessmentTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, assessment_id: UUID) -> str:
        return f'/api/v0/assessments/{assessment_id}/complete/'

    def test_happy_path(self):
        requesting_user_id = self.user.id
        
        assessment = create_assessment(user_id=requesting_user_id)

        # There should be no submission objects
        self.assertEqual(db.AssessmentSubmission.objects.count(), 0)
        
        # Create a submission object by retrieving the assessment for the first time
        response = self.client.get(
            f"/api/v0/assessments/{assessment.id}/",
        )

        assessment_submission = db.AssessmentSubmission.objects.get(
            assessment=assessment,
            user_id=requesting_user_id
        )

        initial_completed_at = assessment_submission.completed_at

        self.assertEqual(assessment.ends_at, initial_completed_at)

        # Complete the assignment
        response = self.client.post(
            self.get_api_endpoint(assessment_id=assessment.id)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        assessment_submission.refresh_from_db()

        # Assessment should be marked as completed before the current datetime
        self.assertGreater(timezone.now(), assessment_submission.completed_at)

        # Assessment should be marked as completed before the initial completed_at
        self.assertGreater(initial_completed_at, assessment_submission.completed_at)
        
    def test_request_after_assessment_completed_throws_error(self):
        requesting_user_id = self.user.id

        assessment = create_assessment(user_id=requesting_user_id)
        
        assessment_submission = create_assessment_submission(
            user_id=requesting_user_id,
            assessment_id=assessment.id
        )

        assessment_submission.completed_at = timezone.now()
        assessment_submission.save()

        response = self.client.post(
            self.get_api_endpoint(assessment_id=assessment.id)
        )

        expected_body = {'error': 'The assessment has already been completed'}
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

    def test_nonexistent_assessment_throws_error(self):
        response = self.client.post(
            self.get_api_endpoint(assessment_id=uuid4())
        )

        expected_body = {'error': 'Assessment submission not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
