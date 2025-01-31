from tests.utils import TestCasesWithUserAuth
import courses.models as db
from django.utils import timezone
from tests.utils import (
    create_quiz,
    create_quiz_submission,
    create_offering,
    create_student_enrollment
)
from rest_framework import status
from uuid import (
    uuid4,
)


class CompleteQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/{course_slug}/quiz/{quiz_slug}/complete/'

    def test_happy_path(self):
        requesting_user_id = self.user.id
        
        quiz = create_quiz(user_id=requesting_user_id)

        # There should be no submission objects
        self.assertEqual(db.QuizSubmission.objects.count(), 0)
        
        # Create a submission object by retrieving the quiz for the first time
        response = self.client.get(
            f"/api/v0/{quiz.offering.course.slug}/quiz/{quiz.slug}/",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        quiz_submission = db.QuizSubmission.objects.get(
            quiz=quiz,
            user_id=requesting_user_id
        )

        initial_completed_at = quiz_submission.completed_at

        self.assertEqual(quiz.ends_at, initial_completed_at)

        # Complete the assignment
        response = self.client.post(
            self.get_api_endpoint(course_slug=quiz.offering.course.slug, quiz_slug=quiz.slug)
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        quiz_submission.refresh_from_db()

        # Quiz should be marked as completed before the current datetime
        self.assertGreater(timezone.now(), quiz_submission.completed_at)

        # Quiz should be marked as completed before the initial completed_at
        self.assertGreater(initial_completed_at, quiz_submission.completed_at)
        
    def test_request_after_quiz_completed_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)
        
        quiz_submission = create_quiz_submission(
            user_id=requesting_user_id,
            quiz=quiz
        )

        quiz_submission.completed_at = timezone.now()
        quiz_submission.save()

        response = self.client.post(
            self.get_api_endpoint(
                quiz_slug=quiz.slug,
                course_slug=quiz.offering.course.slug
            )
        )

        expected_body = {'error': 'The quiz has already been completed'}
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

    def test_nonexistent_quiz_throws_error(self):

        offering = create_offering()
        create_student_enrollment(self.user.id, offering)


        response = self.client.post(
            self.get_api_endpoint(course_slug=offering.course.slug, quiz_slug=uuid4())
        )

        expected_body = {'error': 'Quiz not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
