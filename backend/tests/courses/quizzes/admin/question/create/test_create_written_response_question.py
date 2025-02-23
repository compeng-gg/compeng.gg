from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz
import courses.models as db
from rest_framework import status


class CreateWrittenResponseQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/written_response/create/'

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        prompt = "Written response question prompt"
        points = 1
        order = 1
        max_length = 500

        request_data = {
            "prompt": prompt,
            "points": points,
            "order": order,
            "max_length": max_length,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)