import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from django.db import transaction
from rest_framework import (
    permissions,
    status
)
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from courses.exams.schemas import ExamSerializer
from django.utils import timezone


def get_exam_or_error_response(user_id: int, exam_slug: str) -> db.Exam:
    try:
        exam = db.Exam.objects.get(slug=exam_slug)
    except db.Role.DoesNotExist:
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_exam(request, exam_slug: str):
    request_at = timezone.now()

    user_id = request.user.id

    exam_or_error_response = get_exam_or_error_response(user_id=user_id, exam_slug=exam_slug)

    if isinstance(exam_or_error_response, Response):
        error_response = exam_or_error_response
        return error_response
    
    exam = exam_or_error_response
    
    written_response_questions_prefetch = Prefetch(
        'written_response_questions',
        queryset=db.WrittenResponseQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.WrittenResponseAnswer.objects.filter(
                    exam_submission__user_id=user_id
                )
            )
        )
    )

    coding_questions_prefetch = Prefetch(
        'coding_questions',
        queryset=db.CodingQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.CodingAnswer.objects.filter(
                    exam_submission__user_id=user_id
                )
            )
        )
    )

    multiple_choice_questions_prefetch = Prefetch(
        'multiple_choice_questions',
        queryset=db.MultipleChoiceQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.MultipleChoiceAnswer.objects.filter(
                    exam_submission__user_id=user_id
                )
            )
        )
    )

    checkbox_questions_prefetch = Prefetch(
        'checkbox_questions',
        queryset=db.CheckboxQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.CheckboxAnswer.objects.filter(
                    exam_submission__user_id=user_id
                )
            )
        )
    )

    prefetch_related_objects(
        [exam],
        written_response_questions_prefetch,
        coding_questions_prefetch,
        multiple_choice_questions_prefetch,
        checkbox_questions_prefetch
    )

    with transaction.atomic():
        try:
            exam_submission = db.ExamSubmission.objects.get(
                exam=exam,
                user_id=user_id,
            )

            if (not exam.content_viewable_after_submission
                and exam_submission.completed_at <= timezone.now()):
                return Response(
                    {'error': 'Exam content cannot be viewed after submission'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except db.ExamSubmission.DoesNotExist:
            db.ExamSubmission.objects.create(
                user_id=user_id,
                exam=exam,
                started_at=request_at,
                completed_at=exam.ends_at # Initialize this to the end datetime for the exam
            )

    return Response(data=ExamSerializer(exam).data)
