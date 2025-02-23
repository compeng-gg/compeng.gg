from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz, create_checkbox_question
import courses.models as db
from rest_framework import status


class EditCheckboxQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str, checkbox_question_id) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/edit/checkbox/{checkbox_question_id}/'

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_checkbox_question = create_checkbox_question(
            quiz=mock_quiz,
            correct_option_indices=[1],
        )

        updated_correct_option_indices = [0]

        request_data = {
            "correct_option_indices": updated_correct_option_indices,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, mock_checkbox_question.id),
            data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_checkbox_question.refresh_from_db()

        self.assertEqual(mock_checkbox_question.correct_option_indices, updated_correct_option_indices)

# TODO more tests