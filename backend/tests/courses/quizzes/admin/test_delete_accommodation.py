from tests.utils import TestCasesWithUserAuth, create_quiz, create_user, create_enrollment, create_quiz_accommodation
from rest_framework import status
import courses.models as db


class DeleteAccommodationTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/accommodation/delete/"

    def test_happy_path(self):
        mock_quiz = create_quiz()
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.TA)
        
        user = create_user("student")

        create_quiz_accommodation(user, mock_quiz)

        request_data = {
            "username": user.username,
        }

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Quiz accommodation should no longer exist
        with self.assertRaises(db.QuizAccommodation.DoesNotExist):
            db.QuizAccommodation.objects.get(user=user, quiz=mock_quiz)


