import courses.models as db
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.quizzes.schemas import QuizSerializer
from django.db.models import Prefetch

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_quiz_submissions(request, course_slug: str, quiz_slug: str):
    """
    Retrieve all quiz submissions for a given quiz.
    """

    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure user has instructor or TA role
    user_id = request.user.id
    if not db.Enrollment.objects.filter(
        user_id=user_id, role__offering=quiz.offering, role__kind__in=[db.Role.Kind.INSTRUCTOR, db.Role.Kind.TA]
    ).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Fetch quiz submissions along with user data
    quiz_submissions = db.QuizSubmission.objects.filter(quiz=quiz).select_related("user")

    # Serialize the data
    submission_data = [
        {
            "user_id": submission.user.id,
            "username": submission.user.username,
            "started_at": submission.started_at,
            "completed_at": submission.completed_at,
        }
        for submission in quiz_submissions
    ]

    return Response(data=submission_data, status=status.HTTP_200_OK)
