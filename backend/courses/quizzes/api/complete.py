from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.quizzes.api.permissions import StudentCanTakeQuiz


@api_view(["POST"])
@permission_classes([StudentCanTakeQuiz])
def complete_quiz(request, course_slug: str, quiz_slug: str):
    request_at = timezone.now()

    quiz_submission = request.quiz_submission

    quiz_submission.completed_at = request_at
    quiz_submission.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
