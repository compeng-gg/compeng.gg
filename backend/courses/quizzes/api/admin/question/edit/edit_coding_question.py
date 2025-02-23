from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import CreateCodingQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def edit_coding_question(
    request, course_slug: str, quiz_slug: str, coding_question_id: str
):
    # TODO: validate user is instructor or TA in course
    # TODO: validate quiz matches question
    coding_question = db.CodingQuestion.objects.get(id=coding_question_id)
    serializer = CreateCodingQuestionRequestSerializer(
        coding_question, data=request.data, partial=True
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
