from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz, create_written_response_question, create_coding_question, create_multiple_choice_question, create_checkbox_question
import courses.models as db
from rest_framework import status


class DeleteQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str, question_type: str, checkbox_question_id) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/{question_type}/{checkbox_question_id}/delete/'

    def test_delete_coding_question__happy_path(self):
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_coding_question = create_coding_question(quiz=mock_quiz)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, "coding", mock_coding_question.id),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(db.CodingQuestion.objects.filter(id=mock_coding_question.id).exists())

    def test_delete_multiple_choice_question__happy_path(self):
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_multiple_choice_question = create_multiple_choice_question(quiz=mock_quiz)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, "multiple_choice", mock_multiple_choice_question.id),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(db.MultipleChoiceQuestion.objects.filter(id=mock_multiple_choice_question.id).exists())

    def test_delete_written_response_question__happy_path(self):
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_coding_question = create_written_response_question(quiz=mock_quiz)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, "written_response", mock_coding_question.id),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(db.WrittenResponseQuestion.objects.filter(id=mock_coding_question.id).exists())

    def test_delete_checkbox_question__happy_path(self):
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        mock_coding_question = create_checkbox_question(quiz=mock_quiz)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug, "checkbox", mock_coding_question.id),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(db.CheckboxQuestion.objects.filter(id=mock_coding_question.id).exists())

        