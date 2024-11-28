import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import (
    permissions,
    status
)
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from courses.assessments.schemas import AssessmentSerializer
from django.utils import timezone


def get_assessment_or_error_response(user_id: int, assessment_slug: str) -> db.Assessment:
    try:
        assessment = db.Assessment.objects.get(slug=assessment_slug)
    except db.Role.DoesNotExist:
        raise ValidationError("Assessment does not exist")
    
    try:
        db.Enrollment.objects.get(
            role__kind=db.Role.Kind.STUDENT,
            role__offering=assessment.offering,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise ValidationError("Student is not enrolled in this course")
    
    if assessment.starts_at > timezone.now():
        return Response(
            {'error': 'Assessment has not started yet'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    return assessment


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_assessment(request, assessment_slug: str):
    request_at = timezone.now()

    user_id = request.user.id

    assessment_or_error_response = get_assessment_or_error_response(user_id=user_id, assessment_slug=assessment_slug)

    if isinstance(assessment_or_error_response, Response):
        error_response = assessment_or_error_response
        return error_response
    
    assessment = assessment_or_error_response
    
    written_response_questions_prefetch = Prefetch(
        'written_response_questions',
        queryset=db.WrittenResponseQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.WrittenResponseAnswer.objects.filter(
                    assessment_submission__user_id=user_id
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
                    assessment_submission__user_id=user_id
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
                    assessment_submission__user_id=user_id
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
                    assessment_submission__user_id=user_id
                )
            )
        )
    )

    prefetch_related_objects(
        [assessment],
        written_response_questions_prefetch,
        coding_questions_prefetch,
        multiple_choice_questions_prefetch,
        checkbox_questions_prefetch
    )
    
    assessment_id = assessment.id

    try:
        assessment_submission = db.AssessmentSubmission.objects.get(
            assessment = assessment,
            user_id=user_id,
        )

        if (not assessment.content_viewable_after_submission
            and assessment_submission.completed_at <= timezone.now()):
            return Response(
                {'error': 'Assessment content cannot be viewed after submission'},
                status=status.HTTP_403_FORBIDDEN
            )
    except db.AssessmentSubmission.DoesNotExist:
        db.AssessmentSubmission.objects.create(
            user_id=user_id,
            assessment=assessment,
            started_at=request_at,
            completed_at=assessment.ends_at # Initialize this to the end datetime for the assessment
        )

    return Response(data=AssessmentSerializer(assessment).data)
