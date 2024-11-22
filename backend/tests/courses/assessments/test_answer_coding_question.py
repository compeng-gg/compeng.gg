from tests.utils import (
    TestCasesWithUserAuth,
    create_assessment,
    create_assessment_submission
)
from django.contrib.auth.models import User
import courses.models as db
from datetime import (
    datetime,
    timezone
)
from rest_framework import status
from uuid import (
    UUID,
    uuid4
)


class AnswerCodingQuestion(TestCasesWithUserAuth):
    def get_api_endpoint(self, assessment_id: UUID, coding_question_id: UUID) -> str:
        return f'/api/v0/assessments/{assessment_id}/answer_question/coding/{str(coding_question_id)}/'
    
    def test_no_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        assessment = create_assessment(user_id=requesting_user_id)
        
        assessment_submission = create_assessment_submission(
            user_id=requesting_user_id,
            assessment_id=assessment.id
        )
        
        coding_question = db.CodingQuestion.objects.create(
            assessment=assessment,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        self.assertFalse(db.CodingAnswer.objects.filter(
            assessment_submission=assessment_submission,
            question=coding_question
        ).exists())
        
        response = self.client.post(
            self.get_api_endpoint(
                assessment_id=assessment.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        coding_answer = db.CodingAnswer.objects.get(
            assessment_submission=assessment_submission,
            question=coding_question
        )
        
        self.assertEqual(coding_answer.solution, data['solution'])
        
    def test_existing_answer_obj_happy_path(self):
        requesting_user_id = self.user.id
        
        assessment = create_assessment(user_id=requesting_user_id)
        
        assessment_submission = create_assessment_submission(
            user_id=requesting_user_id,
            assessment_id=assessment.id
        )
        
        coding_question = db.CodingQuestion.objects.create(
            assessment=assessment,
            prompt='Write a function that prints "Hello World!" in Python',
            order=4,
            points=20,
            programming_language=db.CodingQuestion.ProgrammingLanguage.PYTHON,
        )
        
        coding_answer = db.CodingAnswer.objects.create(
            assessment_submission=assessment_submission,
            question=coding_question,
            solution='print("Hi World!")'
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        response = self.client.post(
            self.get_api_endpoint(
                assessment_id=assessment.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        coding_answer.refresh_from_db()
        
        self.assertEqual(coding_answer.solution, data['solution'])

    def test_nonexistent_question_id_throws_error(self):
        requesting_user_id = self.user.id
        
        assessment = create_assessment(user_id=requesting_user_id)
        
        create_assessment_submission(
            user_id=requesting_user_id,
            assessment_id=assessment.id
        )
        
        data = {
            'solution': 'print("Hello World!")'
        }
        
        print(f"Endpint {self.get_api_endpoint(
                assessment_id=assessment.id,
                coding_question_id=uuid4()
            )}")
        
        response = self.client.post(
            self.get_api_endpoint(
                assessment_id=assessment.id,
                coding_question_id=uuid4()
            ), data=data
        )
        
        expected_body = {'error': 'Question not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
        
        exit()
        
    def test_question_id_in_different_offering_throws_error(self):
        other_user_id = User.objects.create().id
        
        assessment = create_assessment(user_id=other_user_id)

        create_assessment_submission(
            user_id=other_user_id,
            assessment_id=assessment.id
        )
        
        coding_question = db.CodingQuestion.objects.create(
            assessment=assessment,
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
                assessment_id=assessment.id,
                coding_question_id=coding_question.id
            ), data=data
        )
        
        expected_body = {'error': 'Question not found'}
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), expected_body)
