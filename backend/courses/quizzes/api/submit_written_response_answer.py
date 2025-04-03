import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import AnswerWrittenResponseQuestionRequestSerializer
from courses.quizzes.api.permissions import StudentCanAnswerQuiz


@api_view(["POST"])
@permission_classes([StudentCanAnswerQuiz])
def submit_written_response_answer(
    request, course_slug: str, quiz_slug: str, written_response_question_id: UUID
):
    request_at = timezone.now()

    serializer = AnswerWrittenResponseQuestionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    quiz_submission = request.quiz_submission
    quiz = request.quiz
    response = serializer.validated_data.get("response")

    try:
        written_response_question = db.WrittenResponseQuestion.objects.get(
            quiz=quiz, id=written_response_question_id
        )
    except db.WrittenResponseQuestion.DoesNotExist:
        return Response(
            {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if (
        written_response_question.max_length is not None
        and len(response) > written_response_question.max_length
    ):
        return Response(
            {
                "error": f"Response length ({len(response)}) is greater than the maximum allowed ({written_response_question.max_length})"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    written_response_answer, created = db.WrittenResponseAnswer.objects.get_or_create(
        quiz_submission=quiz_submission,
        question_id=written_response_question_id,
        defaults={
            "response": response,
            "last_updated_at": request_at,
        },
    )

    if not created:
        written_response_answer.response = response
        written_response_answer.last_updated_at = timezone.now()
        written_response_answer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
