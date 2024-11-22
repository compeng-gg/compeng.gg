import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.assessments.api.utils import get_assessment_submission_or_error_response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_assessment(request, assessment_id: UUID):
    request_at = timezone.now()

    user_id = request.user.id
    
    assessment_submission_or_error_response = get_assessment_submission_or_error_response(
        request_at=request_at, user_id=user_id, assessment_id=assessment_id
    )
    
    if isinstance(assessment_submission_or_error_response, Response):
        error_response = assessment_submission_or_error_response
        return error_response
    
    assessment_submission = assessment_submission_or_error_response
        
    assessment_submission.completed_at = request_at
    assessment_submission.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
