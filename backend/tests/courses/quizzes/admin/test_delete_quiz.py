from tests.utils import TestCasesWithUserAuth, create_enrollment, create_offering, create_repository, create_quiz
import courses.models as db
import responses
from courses.quizzes.api.admin.create_quiz import GITHUB_REPOS_API_BASE
from typing import Optional
from rest_framework import status
from django.contrib.contenttypes.models import ContentType



class CreateQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/delete/'
    
    @responses.activate
    def test_happy_path(self):
        mock_quiz = create_quiz(self.user.id)

        response = self.client.delete(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
