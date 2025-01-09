import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from typing import (
    Optional,
    Union,
    Type
)
from rest_framework.exceptions import ValidationError
from django.utils import timezone



def get_existing_answer_object(
    answer_model: Union[
        Type[db.MultipleChoiceAnswer],
        Type[db.CheckboxAnswer],
        Type[db.CodingAnswer],
        Type[db.WrittenResponseAnswer],
    ],
    question_id: UUID,
    user_id: int,
) -> Optional[
        Union[
            db.MultipleChoiceAnswer,
            db.CheckboxAnswer,
            db.CodingAnswer,
            db.WrittenResponseAnswer,
        ]
    ]:
    try:
        answer_object = answer_model.objects.get(
            question_id=question_id,
            exam_submission__user_id=user_id
        )
        return answer_object
    except answer_model.DoesNotExist:
        return None


def get_exam_submission_or_error_response(
    request_at: datetime, user_id: int, course_slug: str, exam_slug: str
) -> Union[db.ExamSubmission, Response]:
    print("getting submission")
    
        
    exam_or_error_response = get_exam_or_error_response(user_id=user_id, course_slug=course_slug, exam_slug=exam_slug)

    if isinstance(exam_or_error_response, Response):
        error_response = exam_or_error_response
        return error_response
    
    exam = exam_or_error_response

    try:
        exam_submission = db.ExamSubmission.objects.get(
            exam=exam,
            user_id=user_id,
        )
    except db.ExamSubmission.DoesNotExist:
        return Response(
            {'error': 'Exam submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request_at > exam_submission.completed_at:
        return Response(
            {'error': 'The exam has already been completed'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    return exam_submission

def get_exam_or_error_response(user_id: int, course_slug: str, exam_slug: str) -> db.Exam:
    try:
        exam = db.Exam.objects.get(offering__course__slug=course_slug, slug=exam_slug)
    except db.Exam.DoesNotExist:
        raise ValidationError("Exam does not exist")
    
    try:
        db.Enrollment.objects.get(
            role__kind=db.Role.Kind.STUDENT,
            role__offering=exam.offering,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise ValidationError("Student is not enrolled in this course")
    
    if exam.starts_at > timezone.now():
        return Response(
            {'error': 'Exam has not started yet'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    return exam