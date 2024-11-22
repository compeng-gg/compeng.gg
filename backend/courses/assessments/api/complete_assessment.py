import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone


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
        
    assessment_submission.completed_at = timezone.now()
    assessment_submission.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)
