import courses.models as db
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import QuizSerializer
from django.utils import timezone
from courses.quizzes.api.permissions import StudentCanViewQuiz


@api_view(["GET"])
@permission_classes([StudentCanViewQuiz])
def get_questions(request, course_slug: str, quiz_slug: str):
    request_at = timezone.now()
    quiz = request.quiz
    user_id = request.user.id
    accommodation = request.accommodation

    default_completed_at_datetime = (
        quiz.ends_at if accommodation is None else accommodation.ends_at
    )

    quiz_submission, _ = db.QuizSubmission.objects.get_or_create(
        quiz=quiz,
        user_id=user_id,
        defaults={
            "started_at": request_at,
            "completed_at": default_completed_at_datetime,
        },
    )

    return Response(
        data=QuizSerializer(quiz, context={"quiz_submission": quiz_submission}).data
    )
