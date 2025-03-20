from tests.utils import TestCasesWithUserAuth, create_quiz, create_enrollment
import responses
from rest_framework import status
import courses.models as db


class EditQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/edit/"

    @responses.activate
    def test_happy_path(self):
        mock_quiz = create_quiz(self.user.id, quiz_title="Quiz Title")
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.INSTRUCTOR)

        updated_quiz_title = "New Quiz Title"
        updated_quiz_slug = "new-quiz-slug"

        request_data = {
            "visible_at": 1740248155,
            "title": updated_quiz_title,
            "slug": updated_quiz_slug,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_quiz.refresh_from_db()

        self.assertEqual(mock_quiz.visible_at.timestamp(), 1740248155)
        self.assertEqual(mock_quiz.title, updated_quiz_title)
        self.assertEqual(mock_quiz.slug, updated_quiz_slug)
