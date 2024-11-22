import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.assessments.schemas import AnswerCodingQuestionRequestSerializer
from courses.assessments.api.utils import (
    get_assessment_submission_or_error_response,
    get_existing_answer_object
)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_coding_answer(request, assessment_id: UUID, coding_question_id: UUID):
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
    ).exists():
        return Response(
            {'error': 'Question not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
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
            last_updated_at=timezone.now()
        )
    else:
        coding_answer.solution = solution
        coding_answer.last_updated_at=timezone.now()
        coding_answer.save()
        
    return Response(status=status.HTTP_204_NO_CONTENT)
