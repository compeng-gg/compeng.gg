from tests.utils import TestCasesWithUserAuth, create_enrollment, create_quiz
import courses.models as db
from rest_framework import status


class CreateCodingQuestionTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str, quiz_slug: str) -> str:
        return f'/api/v0/quizzes/admin/{course_slug}/{quiz_slug}/coding/create/'

    def test_happy_path(self):
        # Create a quiz and enroll the user as an instructor
        mock_quiz = create_quiz(user_id=self.user.id)
        create_enrollment(user_id=self.user.id, offering=mock_quiz.offering, kind=db.Role.Kind.INSTRUCTOR)

        prompt = "Coding question prompt"
        points = 1
        order = 1
        starter_code = "def solution(): pass"
        programming_language = db.CodingQuestion.ProgrammingLanguage.PYTHON
        files = ["file1.py", "file2.py"]
        file_to_replace = "file1.py"
        grading_file_directory = "grading_tests"

        request_data = {
            "prompt": prompt,
            "points": points,
            "order": order,
            "starter_code": starter_code,
            "programming_language": programming_language,
            "files": files,
            "file_to_replace": file_to_replace,
            "grading_file_directory": grading_file_directory,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug, mock_quiz.slug),
            data=request_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
