from tests.utils import TestCasesWithUserAuth, create_enrollment, create_offering, create_repository, create_quiz
import courses.models as db
import responses
from courses.quizzes.api.admin.api import GITHUB_REPOS_API_BASE
from typing import Optional
from rest_framework import status
from django.contrib.contenttypes.models import ContentType



class CreateMultipleChoiceQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/create/multiple_choice/'
    
    def test_happy_path(self):
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        prompt =  "Multiple choice question prompt"
        points = 1
        order = 1
        options = ["Option 1", "Option 2"]
        correct_option_index = 0

        request_data = {
            "prompt": prompt,
            "points": points,
            "order": order,
            "options": options,
            "correct_option_index": correct_option_index
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data
        )
        print(response.json())

        self.assertEqual(response.status_code, status.HTTP_200_OK)