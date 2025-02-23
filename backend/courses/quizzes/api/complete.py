from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.quizzes.api.utils import get_quiz_submission_or_error_response


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def complete_quiz(request, course_slug: str, quiz_slug: str):
    request_at = timezone.now()

    user_id = request.user.id

    quiz_submission_or_error_response = get_quiz_submission_or_error_response(
        request_at=request_at,
        user_id=user_id,
        quiz_slug=quiz_slug,
        course_slug=course_slug,
    )

    print(quiz_submission_or_error_response)

    if isinstance(quiz_submission_or_error_response, Response):
        error_response = quiz_submission_or_error_response
        return error_response

    quiz_submission = quiz_submission_or_error_response

    quiz_submission.completed_at = request_at
    quiz_submission.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
