from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import (
    MultipleChoiceQuestionRequestSerializer,
)
from rest_framework.response import Response
import courses.models as db


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def edit_multiple_choice_question(
    request, course_slug: str, quiz_slug: str, multiple_choice_question_id: str
):
    # TODO: validate user is instructor or TA in course
    # TODO: validate quiz matches question
    multiple_choice_question = db.MultipleChoiceQuestion.objects.get(
        id=multiple_choice_question_id
    )
    serializer = MultipleChoiceQuestionRequestSerializer(
        multiple_choice_question, data=request.data, partial=True
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
