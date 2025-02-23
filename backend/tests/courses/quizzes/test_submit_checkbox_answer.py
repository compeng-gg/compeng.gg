from tests.utils import TestCasesWithUserAuth, create_quiz, create_quiz_submission
from django.contrib.auth.models import User
import courses.models as db
from django.utils import timezone
from rest_framework import status
from uuid import UUID, uuid4


class SubmitCheckboxAnswerTests(TestCasesWithUserAuth):
    def get_api_endpoint(
        self, course_slug: str, quiz_slug: str, checkbox_question_id: UUID
    ) -> str:
        return f"/api/v0/{course_slug}/quiz/{quiz_slug}/answer/checkbox/{str(checkbox_question_id)}/"

    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        data = {"selected_answer_indices": [0, 2]}

        self.assertFalse(
            db.CheckboxAnswer.objects.filter(
                quiz_submission=quiz_submission, question=checkbox_question
            ).exists()
        )

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        checkbox_answer = db.CheckboxAnswer.objects.get(
            quiz_submission=quiz_submission, question=checkbox_question
        )

        self.assertEqual(
            checkbox_answer.selected_answer_indices, data["selected_answer_indices"]
        )

    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        checkbox_answer = db.CheckboxAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=checkbox_question,
            selected_answer_indices=[0, 1, 2],
            last_updated_at=timezone.now(),
        )

        data = {"selected_answer_indices": [2, 3]}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        checkbox_answer.refresh_from_db()

        self.assertEqual(
            checkbox_answer.selected_answer_indices, data["selected_answer_indices"]
        )

    def test_accepts_empty_array_happy_path(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        checkbox_answer = db.CheckboxAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=checkbox_question,
            selected_answer_indices=[0, 1, 2],
            last_updated_at=timezone.now(),
        )

        data = {"selected_answer_indices": []}
        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        checkbox_answer.refresh_from_db()

        self.assertEqual(
            checkbox_answer.selected_answer_indices, data["selected_answer_indices"]
        )

    def test_negative_answer_index_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        data = {"selected_answer_indices": [2, -1]}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        expected_body = {
            "selected_answer_indices": {
                "1": ["Ensure this value is greater than or equal to 0."]
            }
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected_body)

    def test_negative_answer_index_out_of_bounds_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        data = {"selected_answer_indices": [2, 3, 20]}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        expected_body = {
            "error": f"Maximum index for checkbox question is {len(checkbox_question.options) - 1}"
        }

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), expected_body)

    def test_duplicate_answer_indices_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        data = {"selected_answer_indices": [2, 2]}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        expected_body = {
            "selected_answer_indices": ["Input list must not contain duplicate values"]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected_body)

    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        data = {"selected_answer_index": 0}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=uuid4(),
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

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        data = {"selected_answer_index": 0}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        expected_body = {"error": "Student is not enrolled in this course"}

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

    def test_submission_after_quiz_completed_throws_error(self):
        requesting_user_id = self.user.id

        quiz = create_quiz(user_id=requesting_user_id)

        quiz_submission = create_quiz_submission(user_id=requesting_user_id, quiz=quiz)

        checkbox_question = db.CheckboxQuestion.objects.create(
            quiz=quiz,
            prompt="Choose all positive numbers",
            order=2,
            points=4,
            options=["-1", "-2", "3", "4"],
            correct_option_indices=[2, 3],
        )

        checkbox_answer = db.CheckboxAnswer.objects.create(
            quiz_submission=quiz_submission,
            question=checkbox_question,
            selected_answer_indices=[0, 1, 2],
            last_updated_at=timezone.now(),
        )

        quiz_submission.completed_at = timezone.now()
        quiz_submission.save()

        data = {"selected_answer_indices": [2, 3]}

        response = self.client.post(
            self.get_api_endpoint(
                course_slug=quiz.offering.course.slug,
                quiz_slug=quiz.slug,
                checkbox_question_id=checkbox_question.id,
            ),
            data=data,
        )

        expected_body = {"error": "The quiz has already been completed"}

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)

        checkbox_answer.refresh_from_db()

        self.assertEqual(checkbox_answer.selected_answer_indices, [0, 1, 2])
