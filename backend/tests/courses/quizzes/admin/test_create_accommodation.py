from tests.utils import TestCasesWithUserAuth, create_quiz, create_user, create_enrollment
from rest_framework import status
import courses.models as db


class CreateAccommodationTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/accommodation/create/"

    def test_happy_path(self):
        mock_quiz = create_quiz()
        create_enrollment(self.user.id, mock_quiz.offering, db.Role.Kind.TA)
        
        user = create_user("student")

        visible_at_timestamp = 1740248155
        starts_at_timestamp = 1740248155
        ends_at_timestamp = 1740248155

        request_data = {
            "user": user.id,
            "visible_at": visible_at_timestamp,
            "starts_at": starts_at_timestamp,
            "ends_at": ends_at_timestamp,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        self.assertIn("accommodation_id", response_data)

        accommodation_id = response_data["accommodation_id"]

        quiz_accommodation = db.QuizAccommodation.objects.get(id=accommodation_id)

        self.assertEqual(quiz_accommodation.user.id, user.id)
        self.assertEqual(quiz_accommodation.quiz.id, mock_quiz.id)
        self.assertEqual(quiz_accommodation.visible_at.timestamp(), visible_at_timestamp)
        self.assertEqual(quiz_accommodation.starts_at.timestamp(), starts_at_timestamp)
        self.assertEqual(quiz_accommodation.ends_at.timestamp(), ends_at_timestamp)

    # TODO more tests