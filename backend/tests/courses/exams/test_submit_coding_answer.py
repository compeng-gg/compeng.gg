from tests.utils import (
    TestCasesWithUserAuth,
    create_exam,
    create_exam_submission
)
from django.contrib.auth.models import User
import courses.models as db
from rest_framework import status
from uuid import (
    UUID,
    uuid4
)
from django.utils import timezone


class SubmitCodingAnswerTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, exam_slug: str, coding_question_id: UUID) -> str:
        return f'/api/v0/exams/{exam_slug}/answer/coding/{str(coding_question_id)}/'
    
    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        coding_question = db.CodingQuestion.objects.create(
            exam=exam,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        self.assertFalse(db.CodingAnswer.objects.filter(
            exam_submission=exam_submission,
            question=coding_question
        ).exists())
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        coding_answer = db.CodingAnswer.objects.get(
            exam_submission=exam_submission,
            question=coding_question
        )
        
        self.assertEqual(coding_answer.solution, data['solution'])
        
    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        exam_submission = create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        coding_question = db.CodingQuestion.objects.create(
            exam=exam,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        coding_answer = db.CodingAnswer.objects.create(
            exam_submission=exam_submission,
            question=coding_question,
            solution='print("Hi World!")',
            last_updated_at=timezone.now()
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        coding_answer.refresh_from_db()
        
        self.assertEqual(coding_answer.solution, data['solution'])

    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id
        
        exam = create_exam(user_id=requesting_user_id)
        
        create_exam_submission(
            user_id=requesting_user_id,
            exam_slug=exam.id
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }

        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                coding_question_id=uuid4()
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
        
        coding_question = db.CodingQuestion.objects.create(
            exam=exam,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                coding_question_id=coding_question.id
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
        
        coding_question = db.CodingQuestion.objects.create(
            exam=exam,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        coding_answer = db.CodingAnswer.objects.create(
            exam_submission=exam_submission,
            question=coding_question,
            solution='print("Hi World!")',
            last_updated_at=timezone.now()
        )

        exam_submission.completed_at = timezone.now()
        exam_submission.save()
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                exam_slug=exam.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        expected_body = {'error': 'The exam has already been completed'}
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), expected_body)
        
        coding_answer.refresh_from_db()
        
        self.assertEqual(coding_answer.solution, 'print("Hi World!")')
    