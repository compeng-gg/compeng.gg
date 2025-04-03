import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import AnswerCodingQuestionRequestSerializer
from courses.quizzes.api.permissions import StudentCanAnswerQuiz


@api_view(["POST"])
@permission_classes([StudentCanAnswerQuiz])
def submit_coding_answer(
    request, course_slug: str, quiz_slug: str, coding_question_id: UUID
):
    serializer = AnswerCodingQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    solution = serializer.validated_data.get("solution")

    quiz_submission = request.quiz_submission
    quiz = quiz_submission.quiz

    try:
        db.CodingQuestion.objects.get(quiz=quiz, id=coding_question_id)
    except db.CodingQuestion.DoesNotExist:
        return Response(
            {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
        )

    coding_answer, created = db.CodingAnswer.objects.get_or_create(
        quiz_submission=quiz_submission,
        question_id=coding_question_id,
        defaults={
            "solution": solution,
            "last_updated_at": timezone.now(),
        },
    )

    if not created:
        coding_answer.solution = solution
        coding_answer.last_updated_at = timezone.now()
        coding_answer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
