import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from courses.assessments.schemas import AssessmentSerializer
from dataclasses import dataclass


@dataclass
class AssessmentEnrollmentData:
    assessment: db.Assessment
    enrollment: db.Enrollment


def validate_assessment_enrollment(user_id: int, assessment_id: UUID) -> AssessmentEnrollmentData:
    try:
        assessment = db.Assessment.objects.get(
            id=assessment_id
        )
    except db.Role.DoesNotExist:
        raise ValidationError("Assessment does not exist")
    
    try:
        enrollment = db.Enrollment.objects.get(
            role__kind=db.Role.Kind.STUDENT,
            role__offering=assessment.offering,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise ValidationError("Student is not enrolled in this course")
    
    return AssessmentEnrollmentData(
        assessment=assessment,
        enrollment=enrollment,
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_assessment(request, assessment_id: UUID):
    user_id = request.user.id
    print(f"THe user is is{user_id}")
    print(f"API request.user ID: {request.user.id}")

    assessment_enrollment_data = validate_assessment_enrollment(user_id=user_id, assessment_id=assessment_id)
    enrollment = assessment_enrollment_data.enrollment
    assessment = assessment_enrollment_data.assessment

    written_response_questions_prefetch = Prefetch(
        'written_response_questions',
        queryset=db.WrittenResponseQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.WrittenResponseQuestionAnswer.objects.filter(
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
                queryset=db.CodingQuestionAnswer.objects.filter(
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
                queryset=db.MultipleChoiceQuestionAnswer.objects.filter(
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
                queryset=db.CheckboxQuestionAnswer.objects.filter(
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
        db.AssessmentSubmission.objects.create(
            user_id=user_id,
            assessment_id=assessment_id,
            start_datetime=datetime.now(),
        )

    return Response(
        data=AssessmentSerializer(assessment).data
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_multiple_choice_question(request, question_id: UUID):
    pass


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_checkbox_question(request, assessment_id: UUID):
    pass


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_written_response_question(request, assessment_id: UUID):
    pass

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_coding_question(request, assessment_id: UUID):
    pass