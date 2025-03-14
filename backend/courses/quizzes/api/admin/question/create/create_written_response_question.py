from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import (
    WrittenResponseQuestionRequestSerializer,
)
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_written_response_question(request, course_slug: str, quiz_slug: str):
    serializer = WrittenResponseQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    max_length = serializer.validated_data.get("max_length")

    written_response_question = db.WrittenResponseQuestion.objects.create(
        prompt=prompt,
        points=points,
        order=order,
        max_length=max_length,
        quiz=request.quiz,
    )

    return Response(
        status=status.HTTP_200_OK, data={"question_id": written_response_question.id}
    )
