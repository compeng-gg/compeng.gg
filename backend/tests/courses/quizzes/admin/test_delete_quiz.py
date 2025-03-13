from tests.utils import TestCasesWithUserAuth, create_quiz, create_enrollment
import responses
from rest_framework import status
import courses.models as db


class DeleteQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/delete/"

    @responses.activate
    def test_happy_path(self):
        mock_quiz = create_quiz(self.user.id)
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.INSTRUCTOR)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
