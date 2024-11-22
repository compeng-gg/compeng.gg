import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.assessments.schemas import AnswerWrittenResponseQuestionRequestSerializer
from courses.assessments.api.utils import (
    get_assessment_submission_or_error_response,
    get_existing_answer_object
)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_written_response_answer(request, assessment_id: UUID, written_response_question_id: UUID):
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
            last_updated_at=timezone.now()
        )
    else:
        written_response_answer.response = response
        written_response_answer.last_updated_at = timezone.now()
        written_response_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
