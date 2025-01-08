import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.exams.schemas import AnswerWrittenResponseQuestionRequestSerializer
from courses.exams.api.utils import (
    get_exam_submission_or_error_response,
    get_existing_answer_object
)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_written_response_answer(request, exam_slug: str, written_response_question_id: UUID):
    request_at = timezone.now()
    
    serializer = AnswerWrittenResponseQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    response = serializer.validated_data.get('response')
    
    exam_submission_or_error_response = get_exam_submission_or_error_response(
        request_at=request_at, user_id=user_id, exam_slug=exam_slug
    )
    
    if isinstance(exam_submission_or_error_response, Response):
        error_response = exam_submission_or_error_response
        return error_response
    
    exam_submission = exam_submission_or_error_response
    
    written_response_answer = get_existing_answer_object(
        answer_model=db.WrittenResponseAnswer,
        question_id=written_response_question_id,
        user_id=user_id,
    )

    

    ### Validate selected checkbox indices are valid
    try:
        written_response_question = db.WrittenResponseQuestion.objects.get(
            exam__slug=exam_slug,
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
            exam_submission=exam_submission,
            question_id=written_response_question_id,
            response=response,
            last_updated_at=timezone.now()
        )
    else:
        written_response_answer.response = response
        written_response_answer.last_updated_at = timezone.now()
        written_response_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
