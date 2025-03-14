from tests.utils import TestCasesWithUserAuth, create_quiz, create_quiz_submission
from django.contrib.auth.models import User
import courses.models as db
from django.utils import timezone
from rest_framework import status
from uuid import UUID, uuid4


class SubmitWrittenResponseAnswerTests(TestCasesWithUserAuth):
    def get_api_endpoint(
        self, course_slug: str, quiz_slug: str, written_response_question_id: UUID
    ) -> str:
        return f"/api/v0/{course_slug}/quiz/{quiz_slug}/answer/written_response/{str(written_response_question_id)}/"

    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        written_response_question = db.WrittenResponseQuestion.objects.create(
            quiz=quiz, prompt="Write a poem", order=1, points=5, max_length=None
        )

        data = {"response": "This is a test."}

        self.assertFalse(
            db.WrittenResponseAnswer.objects.filter(
                quiz_submission=quiz_submission, question=written_response_question
            ).exists()
        )

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        written_response_answer = db.WrittenResponseAnswer.objects.get(
            quiz_submission=quiz_submission, question=written_response_question
        )

        self.assertEqual(written_response_answer.response, data["response"])

    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        written_response_question = db.WrittenResponseQuestion.objects.create(
            quiz=quiz, prompt="Write a poem", order=1, points=5, max_length=None
        )

        written_response_answer = db.WrittenResponseAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=written_response_question,
            response="Noooooo",
            last_updated_at=timezone.now(),
        )

        data = {"response": "This is a test."}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        written_response_answer.refresh_from_db()

        self.assertEqual(written_response_answer.response, data["response"])

    def test_response_longer_than_max_length_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        written_response_question = db.WrittenResponseQuestion.objects.create(
            quiz=quiz, prompt="Write a poem", order=1, points=5, max_length=26
        )

        valid_data = {"response": "This is exactly the limit!"}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
            ),
            data=valid_data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        written_response_answer = db.WrittenResponseAnswer.objects.get(
            quiz_submission=quiz_submission, question=written_response_question
        )

        self.assertEqual(written_response_answer.response, valid_data["response"])

        invalid_data = {"response": "This is over the limit by 1"}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
            ),
            data=invalid_data,
        )

        expected_body = {
            "error": f"Response length ({len(invalid_data['response'])}) is greater than the maximum allowed ({written_response_question.max_length})"
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_body)

        written_response_answer.refresh_from_db()

        self.assertEqual(written_response_answer.response, valid_data["response"])

    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        data = {"response": "This is a test."}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=uuid4(),
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

        written_response_question = db.WrittenResponseQuestion.objects.create(
            quiz=quiz, prompt="Write a poem", order=1, points=5, max_length=None
        )

        data = {"response": "This is a test."}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
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

        written_response_question = db.WrittenResponseQuestion.objects.create(
            quiz=quiz, prompt="Write a poem", order=1, points=5, max_length=None
        )

        written_response_answer = db.WrittenResponseAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=written_response_question,
            response="Noooooo",
            last_updated_at=timezone.now(),
        )

        quiz_submission.completed_at = timezone.now()
        quiz_submission.save()

        data = {"response": "This is a test."}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                written_response_question_id=written_response_question.id,
            ),
            data=data,
        )

        expected_body = {"detail": "Quiz has already been completed"}

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

        written_response_answer.refresh_from_db()

        self.assertEqual(written_response_answer.response, "Noooooo")
