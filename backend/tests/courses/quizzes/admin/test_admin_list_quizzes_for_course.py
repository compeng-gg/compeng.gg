from tests.utils import TestCasesWithUserAuth, create_offering, create_quiz, create_enrollment
import responses
from rest_framework import status
import courses.models as db


class ListQuizzesForCourseTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/"

    @responses.activate
    def test_happy_path(self):
        mock_offering = create_offering()

        create_enrollment(
            user_id=self.user.id,
            offering=mock_offering,
            kind=db.Role.Kind.INSTRUCTOR
        )

        create_quiz(
            offering=mock_offering,
            quiz_title="Midterm",
            quiz_slug="midterm",
            repository_full_name="user/midterm_repo",
            repository_id=1,
        )

        create_quiz(
            offering=mock_offering,
            quiz_title="Final Exam",
            quiz_slug="final-exam",
            repository_full_name="user/final_exam_repo",
            repository_id=2,
        )
        
        response = self.client.get(self.get_api_endpoint(mock_offering.course.slug))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
