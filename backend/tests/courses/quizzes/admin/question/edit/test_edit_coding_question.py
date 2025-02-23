from tests.utils import (
    TestCasesWithUserAuth,
    create_enrollment,
    create_quiz,
    create_coding_question,
)
import courses.models as db
from rest_framework import status


class EditCodingQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(
        self, course_slug: str, quiz_slug: str, coding_question_id
    ) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/coding/{coding_question_id}/edit/"

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(
            user_id=self.user.id,
            offering=mock_quiz.offering,
            kind=db.Role.Kind.INSTRUCTOR,
        )

        mock_coding_question = create_coding_question(
            quiz=mock_quiz,
            programming_lanaguage=db.CodingQuestion.ProgrammingLanguage.C_PP,
        )

        updated_programming_language = db.CodingQuestion.ProgrammingLanguage.C_PP

        request_data = {
            "programming_language": updated_programming_language,
        }

        response = self.client.post(
            self.get_api_endpoint(
                mock_quiz.offering.course.slug, mock_quiz.slug, mock_coding_question.id
            ),
            data=request_data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_coding_question.refresh_from_db()

        self.assertEqual(
            mock_coding_question.programming_language, updated_programming_language
        )


# TODO more tests
