from tests.utils import TestCasesWithUserAuth, create_quiz
import responses
from rest_framework import status


class DeleteQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/delete/"

    @responses.activate
    def test_happy_path(self):
        mock_quiz = create_quiz(self.user.id)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
