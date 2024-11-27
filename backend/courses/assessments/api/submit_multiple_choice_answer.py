import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.assessments.schemas import AnswerMultipleChoiceQuestionRequestSerializer
from courses.assessments.api.utils import (
    get_assessment_submission_or_error_response,
    get_existing_answer_object
)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_multiple_choice_answer(request, assessment_slug: str, multiple_choice_question_id: UUID):
    request_at = timezone.now()
    
    serializer = AnswerMultipleChoiceQuestionRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    selected_answer_index = serializer.validated_data.get('selected_answer_index')
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        request_at=request_at, user_id=user_id, assessment_slug=assessment_slug
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
            last_updated_at=timezone.now()
        )
    else:
        multiple_choice_answer.selected_answer_index = selected_answer_index
        multiple_choice_answer.last_updated_at = timezone.now()
        multiple_choice_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
