import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import (
    status,
    permissions
)
from rest_framework.decorators import api_view, permission_classes
from courses.exams.schemas import AnswerCheckboxQuestionRequestSerializer
from courses.exams.api.utils import (
    get_exam_submission_or_error_response,
    get_existing_answer_object
)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_checkbox_answer(request, exam_slug: str, checkbox_question_id: UUID):
    request_at = timezone.now()
    
    serializer = AnswerCheckboxQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id
    selected_answer_indices = serializer.validated_data.get('selected_answer_indices')
    
    exam_submission_or_error_response = get_exam_submission_or_error_response(
        request_at=request_at, user_id=user_id, exam_slug=exam_slug
    )
    
    if isinstance(exam_submission_or_error_response, Response):
        error_response = exam_submission_or_error_response
        return error_response
    
    exam_submission = exam_submission_or_error_response
    
    checkbox_answer = get_existing_answer_object(
        answer_model=db.CheckboxAnswer,
        question_id=checkbox_question_id,
        user_id=user_id,
    )

    ### Validate selected checkbox indices are valid
    try:
        checkbox_question = db.CheckboxQuestion.objects.get(
            exam_slug=exam_slug,
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
            exam_submission=exam_submission,
            question_id=checkbox_question_id,
            selected_answer_indices=selected_answer_indices,
            last_updated_at=timezone.now()
        )
    else:
        checkbox_answer.selected_answer_indices = selected_answer_indices
        checkbox_answer.last_updated_at=timezone.now()
        checkbox_answer.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
