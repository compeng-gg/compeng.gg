from tests.utils import (
    TestCasesWithUserAuth,
    create_exam,
    create_exam_submission
)
from django.contrib.auth.models import User
import courses.models as db
from django.utils import timezone
from rest_framework import status
from uuid import (
    UUID,
    uuid4
)


class SubmitMultipleChoiceAnswerTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, exam_slug: str, multiple_choice_question_id: UUID) -> str:
        return f'/api/v0/exams/{exam_slug}/answer/multiple_choice/{str(multiple_choice_question_id)}/'
    
    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        data = {
            'selected_answer_index': 0
        }
        
        self.assertFalse(db.MultipleChoiceAnswer.objects.filter(
            exam_submission=exam_submission,
            question=multiple_choice_question
        ).exists())
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        multiple_choice_answer = db.MultipleChoiceAnswer.objects.get(
            exam_submission=exam_submission,
            question=multiple_choice_question
        )
        
        self.assertEqual(multiple_choice_answer.selected_answer_index, 0)
        
    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        multiple_choice_answer = db.MultipleChoiceAnswer.objects.create(
            exam_submission=exam_submission,
            question=multiple_choice_question,
            selected_answer_index=0,
            last_updated_at=timezone.now()
        )
        
        data = {
            'selected_answer_index': 1
        }

        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        multiple_choice_answer.refresh_from_db()
        
        self.assertEqual(multiple_choice_answer.selected_answer_index, 1)
        
    def test_negative_answer_index_throws_error(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        data = {
            'selected_answer_index': -1
        }

        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )
        
        expected_body = {'selected_answer_index': ['The selected answer index must not be negative']}
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), expected_body)
        
    def test_answer_index_out_of_bounds_throws_error(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        data = {
            'selected_answer_index': 3
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )

        expected_body = {'error': f'Maximum index for multiple choice question is {len(multiple_choice_question.options) - 1}'}
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), expected_body)
        
    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        data = {
            'selected_answer_index': 0
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=uuid4()
            ), data=data
        )
        
        expected_body = {'error': 'Question not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
        
    def test_exam_in_different_offering_throws_error(self):
        other_user_id = User.objects.create().id
        
        exam = create_exam(user_id=other_user_id)

        create_exam_submission(
            user_id=other_user_id,
            exam_slug=exam.id
        )
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        data = {
            'selected_answer_index': 0
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )
        
        expected_body = {'error': 'Exam submission not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)

    def test_submission_after_exam_completed_throws_error(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
            exam=exam,
            prompt='Choose the animal that flies',
            order=1,
            points=3,
            options=[
                'Deer',
                'Bird',
                'Shark'
            ],
            correct_option_index=1
        )
        
        multiple_choice_answer = db.MultipleChoiceAnswer.objects.create(
            exam_submission=exam_submission,
            question=multiple_choice_question,
            selected_answer_index=0,
            last_updated_at=timezone.now()
        )
        
        exam_submission.completed_at = timezone.now()
        exam_submission.save()

        data = {
            'selected_answer_index': 1
        }

        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                multiple_choice_question_id=multiple_choice_question.id
            ), data=data
        )
        
        expected_body = {'error': 'The exam has already been completed'}
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)
        
        multiple_choice_answer.refresh_from_db()
        
        self.assertEqual(multiple_choice_answer.selected_answer_index, 0)
    