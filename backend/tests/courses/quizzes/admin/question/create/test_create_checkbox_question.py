from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz
import courses.models as db
from rest_framework import status


class CreateCheckboxQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/checkbox/create/'

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        prompt = "Checkbox question prompt"
        points = 1
        order = 1
        options = ["Option 1", "Option 2", "Option 3"]
        correct_option_indices = [0, 2]

        request_data = {
            "prompt": prompt,
            "points": points,
            "order": order,
            "options": options,
            "correct_option_indices": correct_option_indices
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
