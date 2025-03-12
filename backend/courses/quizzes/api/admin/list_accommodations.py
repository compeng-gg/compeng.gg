from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import QuizAccommodationListItemSerializer
from rest_framework.response import Response
from courses.quizzes.api.admin.utils import (
    validate_user_is_ta_or_instructor_in_course,
    CustomException,
)
import courses.models as db


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_quiz_accommodations(request, course_slug: str, quiz_slug: str):
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

    accommodations = db.QuizAccommodation.objects.filter(quiz=quiz)

    serializer = QuizAccommodationListItemSerializer(
        accommodations,
        many=True,
    )

    return Response(
        status=status.HTTP_200_OK, data={"quiz_accommodations": serializer.data}
    )
