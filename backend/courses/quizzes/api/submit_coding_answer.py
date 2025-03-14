import courses.models as db
from uuid import UUID
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import AnswerCodingQuestionRequestSerializer
from courses.quizzes.api.utils import (
    get_existing_answer_object,
)
from typing import Optional
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

    user_id = request.user.id
    quiz_submission = request.quiz_submission

    if not db.CodingQuestion.objects.filter(
        quiz__slug=quiz_slug, id=coding_question_id
    ).exists():
        return Response(
            {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
        )

    coding_answer: Optional[db.CodingAnswer] = get_existing_answer_object(
        answer_model=db.CodingAnswer, question_id=coding_question_id, user_id=user_id
    )

    if coding_answer is None:
        db.CodingAnswer.objects.create(
            quiz_submission=quiz_submission,
            question_id=coding_question_id,
            solution=solution,
            last_updated_at=timezone.now(),
        )
    else:
        coding_answer.solution = solution
        coding_answer.last_updated_at = timezone.now()
        coding_answer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
