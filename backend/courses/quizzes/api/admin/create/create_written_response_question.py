from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import (
    CreateWrittenResponseQuestionRequestSerializer,
)
from rest_framework.response import Response
from django.db.models import Q
import courses.models as db


class CustomException(Exception):
    pass


def validate_user_is_ta_or_instructor_in_course(user_id: int, course_slug: str) -> None:
    try:
        db.Enrollment.objects.get(
            (Q(role__kind=db.Role.Kind.TA) | Q(role__kind=db.Role.Kind.INSTRUCTOR)),
            role__offering__course__slug=course_slug,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise CustomException("User is not a TA or Instructor in this course")


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_written_response_question(request, course_slug: str, quiz_slug: str):
    serializer = CreateWrittenResponseQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id

    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    max_length = serializer.validated_data.get("max_length")

    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)

    written_response_question = db.WrittenResponseQuestion.objects.create(
        prompt=prompt,
        points=points,
        order=order,
        max_length=max_length,
        quiz=quiz,
    )

    return Response(
        status=status.HTTP_200_OK, data={"question_id": written_response_question.id}
    )
