from tests.utils import TestCasesWithUserAuth
import courses.models as db
from django.utils import timezone
from tests.utils import (
    create_exam,
    create_exam_submission
)
from rest_framework import status
from uuid import (
    uuid4,
    UUID
)


class CompleteExamTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, exam_slug: str) -> str:
        return f'/api/v0/exams/{exam_slug}/complete/'

    def test_happy_path(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)

        # There should be no submission objects
        self.assertEqual(db.ExamSubmission.objects.count(), 0)
        
        # Create a submission object by retrieving the exam for the first time
        response = self.client.get(
            f"/api/v0/exams/{exam.id}/",
        )

        exam_submission = db.ExamSubmission.objects.get(
            exam=exam,
            user_id=requesting_user_id
        )

        initial_completed_at = exam_submission.completed_at

        self.assertEqual(exam.ends_at, initial_completed_at)

        # Complete the assignment
        response = self.client.post(
            self.get_api_endpoint(exam_slug=exam.id)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        exam_submission.refresh_from_db()

        # Exam should be marked as completed before the current datetime
        self.assertGreater(timezone.now(), exam_submission.completed_at)

        # Exam should be marked as completed before the initial completed_at
        self.assertGreater(initial_completed_at, exam_submission.completed_at)
        
    def test_request_after_exam_completed_throws_error(self):
        requesting_user_id = self.user.id

        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )

        exam_submission.completed_at = timezone.now()
        exam_submission.save()

        response = self.client.post(
            self.get_api_endpoint(exam_slug=exam.id)
        )

        expected_body = {'error': 'The exam has already been completed'}
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

    def test_nonexistent_exam_throws_error(self):
        response = self.client.post(
            self.get_api_endpoint(exam_slug=uuid4())
        )

        expected_body = {'error': 'Exam submission not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
