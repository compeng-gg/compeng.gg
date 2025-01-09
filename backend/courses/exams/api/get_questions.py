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
from courses.exams.schemas import ExamSerializer
from django.utils import timezone
from typing import Optional


def get_exam(user_id: int, course_slug: str, exam_slug: str) -> Optional[db.Exam]:
    try:
        exam = db.Exam.objects.get(slug=exam_slug, offering__course__slug=course_slug)
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
def get_questions(request, course_slug: str, exam_slug: str):
    request_at = timezone.now()

    user_id = request.user.id

    exam = get_exam(user_id, course_slug, exam_slug)

    if exam is None:
        return Response(
            data={'error': f'Exam not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
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

    print("HELLO")
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

    print("HELLO")
    return Response(data=ExamSerializer(exam).data)
