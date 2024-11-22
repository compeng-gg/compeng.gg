import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from courses.assessments.schemas import (
    AssessmentSerializer,
    AnswerMultipleChoiceQuestionRequestSerializer,
    AnswerWrittenResponseQuestionRequestSerializer,
    AnswerCheckboxQuestionRequestSerializer,
    AnswerCodingQuestionRequestSerializer,
)
from dataclasses import dataclass
from typing import (
    Optional,
    Union,
    Type,
)


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
            assessment_submission__user_id=user_id
        )
        return answer_object
    except answer_model.DoesNotExist:
        return None


def get_assessment_submission_or_error_response(
    answered_at: datetime, user_id: int, assessment_id: UUID
) -> Union[db.AssessmentSubmission, Response]:
    try:
        assessment_submission = db.AssessmentSubmission.objects.get(
            assessment_id=assessment_id,
            user_id=user_id,
        )
    except db.AssessmentSubmission.DoesNotExist:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    if answered_at > assessment_submission.completed_at:
        return Response(
            {'error': 'The assessment has already been completed'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    return assessment_submission


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_multiple_choice_question(request, assessment_id: UUID, multiple_choice_question_id: UUID):
    answered_at = timezone.now()
    
    serializer = AnswerMultipleChoiceQuestionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    selected_answer_index = serializer.validated_data.get('selected_answer_index')
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        answered_at=answered_at, user_id=user_id, assessment_id=assessment_id
    )
    
    if isinstance(assessment_submission_or_error_response, Response):
        error_response = assessment_submission_or_error_response
        return error_response
    
    assessment_submission = assessment_submission_or_error_response
    
    multiple_choice_answer = get_existing_answer_object(
        answer_model=db.MultipleChoiceAnswer,
        question_id=multiple_choice_question_id,
        user_id=user_id,
    )
            
    ### Validate selected multiple choice index is valid
    try:
        multiple_choice_question = db.MultipleChoiceQuestion.objects.get(
            id=multiple_choice_question_id,
        )
    except db.MultipleChoiceQuestion.DoesNotExist:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    max_option_index = len(multiple_choice_question.options) - 1
    
    if selected_answer_index > max_option_index:
        return Response(
            {'error': f'Maximum index for multiple choice question is {max_option_index}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if multiple_choice_answer is None:
        db.MultipleChoiceAnswer.objects.create(
            assessment_submission=assessment_submission,
            question_id=multiple_choice_question_id,
            selected_answer_index=selected_answer_index,
        )
    else:
        multiple_choice_answer.selected_answer_index = selected_answer_index
        multiple_choice_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_checkbox_question(request, assessment_id: UUID, checkbox_question_id: UUID):
    answered_at = timezone.now()
    
    serializer = AnswerCheckboxQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    selected_answer_indices = serializer.validated_data.get('selected_answer_indices')
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        answered_at=answered_at, user_id=user_id, assessment_id=assessment_id
    )
    
    if isinstance(assessment_submission_or_error_response, Response):
        error_response = assessment_submission_or_error_response
        return error_response
    
    assessment_submission = assessment_submission_or_error_response
    
    checkbox_answer = get_existing_answer_object(
        answer_model=db.CheckboxAnswer,
        question_id=checkbox_question_id,
        user_id=user_id,
    )

    ### Validate selected checkbox indices are valid
    try:
        checkbox_question = db.CheckboxQuestion.objects.get(
            assessment_id=assessment_id,
            id=checkbox_question_id
        )
    except db.CheckboxQuestion.DoesNotExist:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    max_option_index = len(checkbox_question.options) - 1
    
    selected_answer_indices = [] if selected_answer_indices is None else selected_answer_indices
    
    if any(selected_option_index > max_option_index for selected_option_index in selected_answer_indices):
        return Response(
            {'error': f'Maximum index for checkbox question is {max_option_index}'},
            status=status.HTTP_404_NOT_FOUND
        )
            
    if checkbox_answer is None:
        db.CheckboxAnswer.objects.create(
            assessment_submission=assessment_submission,
            question_id=checkbox_question_id,
            selected_answer_indices=selected_answer_indices,
        )
    else:
        checkbox_answer.selected_answer_indices = selected_answer_indices
        checkbox_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_written_response_question(request, assessment_id: UUID, written_response_question_id: UUID):
    answered_at = timezone.now()
    
    serializer = AnswerWrittenResponseQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    response = serializer.validated_data.get('response')
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        answered_at=answered_at, user_id=user_id, assessment_id=assessment_id
    )
    
    if isinstance(assessment_submission_or_error_response, Response):
        error_response = assessment_submission_or_error_response
        return error_response
    
    assessment_submission = assessment_submission_or_error_response
    
    written_response_answer = get_existing_answer_object(
        answer_model=db.WrittenResponseAnswer,
        question_id=written_response_question_id,
        user_id=user_id,
    )
            
    ### Validate selected checkbox indices are valid
    try:
        written_response_question = db.WrittenResponseQuestion.objects.get(
            assessment_id=assessment_id,
            id=written_response_question_id
        )
    except db.WrittenResponseQuestion.DoesNotExist:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if written_response_question.max_length is not None and len(response) > written_response_question.max_length:
        return Response(
            {'error': f'Response length ({len(response)}) is greater than the maximum allowed ({written_response_question.max_length})'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if written_response_answer is None:
        db.WrittenResponseAnswer.objects.create(
            assessment_submission=assessment_submission,
            question_id=written_response_question_id,
            response=response,
        )
    else:
        written_response_answer.response = response
        written_response_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def answer_coding_question(request, assessment_id: UUID, coding_question_id: UUID):
    answered_at = timezone.now()
    
    serializer = AnswerCodingQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    solution = serializer.validated_data.get('solution')
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        answered_at=answered_at, user_id=user_id, assessment_id=assessment_id
    )
    
    if isinstance(assessment_submission_or_error_response, Response):
        error_response = assessment_submission_or_error_response
        return error_response
    
    assessment_submission = assessment_submission_or_error_response
    
    print(db.CodingQuestion.objects.count())
    
    if not db.CodingQuestion.objects.filter(
        assessment_id=assessment_id,
        id=coding_question_id
    ).exists:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    print(f"it sexist")
    print(assessment_id)
    print(coding_question_id)
    
    """try:
        written_response_question = db.CodingQuestion.objects.get(
            assessment_id=assessment_id,
            id=coding_question_id
        )
    except db.CodingQuestion.DoesNotExist:
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )"""
        
    print("dd")
    
    coding_answer = get_existing_answer_object(
        answer_model=db.CodingAnswer,
        question_id=coding_question_id,
        user_id=user_id
    )
    
    if coding_answer is None:
        db.CodingAnswer.objects.create(
            assessment_submission=assessment_submission,
            question_id=coding_question_id,
            solution=solution,
        )
    else:
        coding_answer.solution = solution
        coding_answer.save()
        
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_assessment(request, assessment_id: UUID):
    user_id = request.user.id
    
    try:
        assessment_submission = db.AssessmentSubmission.objects.get(
            assessment_id=assessment_id,
            user_id=user_id,
        )
    except db.AssessmentSubmission.DoesNotExist:
        return Response(
            {'error': 'Assessment does not exist, or user did not start this assessment yet'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    assessment_submission.completed_at = datetime.now()
    assessment_submission.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
    