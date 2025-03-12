from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import QuizAccommodationSerializer
from rest_framework.response import Response
from courses.quizzes.api.admin.utils import (
    validate_user_is_ta_or_instructor_in_course,
    CustomException,
)
import courses.models as db


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_quiz_accommodation(request, course_slug: str, quiz_slug: str):
    user_id = request.user.id
    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response(
            {"error": "Quiz does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data.copy()
    data["quiz"] = quiz.id

    serializer = QuizAccommodationSerializer(data=data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(
        status=status.HTTP_200_OK, data={"accommodation_id": serializer.instance.id}
    )
