import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.exams.api.utils import get_exam_submission_or_error_response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_exam(request, exam_slug: str):
    request_at = timezone.now()

    user_id = request.user.id
    
    exam_submission_or_error_response = get_exam_submission_or_error_response(
        request_at=request_at, user_id=user_id, exam_slug=exam_slug
    )
    
    if isinstance(exam_submission_or_error_response, Response):
        error_response = exam_submission_or_error_response
        return error_response
    
    exam_submission = exam_submission_or_error_response
        
    exam_submission.completed_at = request_at
    exam_submission.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
