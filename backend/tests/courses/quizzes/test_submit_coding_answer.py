from tests.utils import (
    TestCasesWithUserAuth,
    create_quiz,
    create_quiz_submission,
    create_coding_question,
)
from django.contrib.auth.models import User
import courses.models as db
from rest_framework import status
from uuid import UUID, uuid4
from django.utils import timezone


class SubmitCodingAnswerTests(TestCasesWithUserAuth):
    def get_api_endpoint(
        self, course_slug: str, quiz_slug: str, coding_question_id: UUID
    ) -> str:
        return f"/api/v0/{course_slug}/quiz/{quiz_slug}/answer/coding/{str(coding_question_id)}/"

    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        coding_question = create_coding_question(quiz=quiz)

        data = {"solution": 'print("Hello World!")'}

        self.assertFalse(
            db.CodingAnswer.objects.filter(
                quiz_submission=quiz_submission, question=coding_question
            ).exists()
        )

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                coding_question_id=coding_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        coding_answer = db.CodingAnswer.objects.get(
            quiz_submission=quiz_submission, question=coding_question
        )

        self.assertEqual(coding_answer.solution, data["solution"])

    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        coding_question = create_coding_question(quiz=quiz)

        coding_answer = db.CodingAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=coding_question,
            solution='print("Hi World!")',
            last_updated_at=timezone.now(),
        )

        data = {"solution": 'print("Hello World!")'}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                coding_question_id=coding_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        coding_answer.refresh_from_db()

        self.assertEqual(coding_answer.solution, data["solution"])

    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        data = {"solution": 'print("Hello World!")'}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                coding_question_id=uuid4(),
            ),
            data=data,
        )

        expected_body = {"error": "Question not found"}

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)

    def test_quiz_in_different_offering_throws_error(self):
        other_user_id = User.objects.create().id

        quiz = create_quiz(user_id=other_user_id)

        create_quiz_submission(user_id=other_user_id, quiz=quiz)

        coding_question = create_coding_question(quiz=quiz)

        data = {"solution": 'print("Hello World!")'}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                coding_question_id=coding_question.id,
            ),
            data=data,
        )

        expected_body = {"detail": "Student is not enrolled in this course"}

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

    def test_submission_after_quiz_completed_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        coding_question = create_coding_question(quiz=quiz)

        coding_answer = db.CodingAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=coding_question,
            solution='print("Hi World!")',
            last_updated_at=timezone.now(),
        )

        quiz_submission.completed_at = timezone.now()
        quiz_submission.save()

        data = {"solution": 'print("Hello World!")'}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                coding_question_id=coding_question.id,
            ),
            data=data,
        )

        expected_body = {"detail": "Quiz has already been completed"}

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

        coding_answer.refresh_from_db()

        self.assertEqual(coding_answer.solution, 'print("Hi World!")')
