from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz, create_written_response_question
import courses.models as db
from rest_framework import status


class EditWrittenResponseQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str, written_response_question_id) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/edit/written_response/{written_response_question_id}/'

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_written_response_question = create_written_response_question(
            quiz=mock_quiz,
            max_length=200
        )

        updated_max_length = 300

        request_data = {
            "max_length": updated_max_length,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, mock_written_response_question.id),
            data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_written_response_question.refresh_from_db()

        self.assertEqual(mock_written_response_question.max_length, updated_max_length)

# TODO more tests