import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from courses.assessments.schemas import AssessmentSerializer


def validate_assessment_enrollment(user_id: int, assessment_id: UUID) -> db.Assessment:
    try:
        assessment = db.Assessment.objects.get(
            id=assessment_id
        )
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
    
    return assessment


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_assessment(request, assessment_id: UUID):
    user_id = request.user.id

    assessment = validate_assessment_enrollment(user_id=user_id, assessment_id=assessment_id)

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

    if not db.AssessmentSubmission.objects.filter(
        assessment_id=assessment_id,
        user_id=user_id,
    ).exists():
        # Create a submission object when assessment is first viewed
        db.AssessmentSubmission.objects.create(
            user_id=user_id,
            assessment_id=assessment_id,
            started_at=datetime.now(),
            completed_at=assessment.ends_at # Initialize this to the end datetime for the assessment
        )

    return Response(
        data=AssessmentSerializer(assessment).data
    )
