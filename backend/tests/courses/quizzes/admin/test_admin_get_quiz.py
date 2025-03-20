from tests.utils import TestCasesWithUserAuth, create_quiz, create_checkbox_question, create_coding_question, create_written_response_question, create_multiple_choice_question, create_enrollment
import responses
from rest_framework import status
import courses.models as db


class GetQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/"

    @responses.activate
    def test_happy_path(self):
        mock_quiz = create_quiz(self.user.id, quiz_title="Quiz Title")
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.INSTRUCTOR)
        
        create_checkbox_question(mock_quiz, order=2)
        create_coding_question(mock_quiz, order=3)
        create_written_response_question(mock_quiz, order=4)
        create_multiple_choice_question(mock_quiz, order=1)

        response = self.client.get(self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
