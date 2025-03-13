from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.utils import (
    validate_user_is_ta_or_instructor_in_course,
    CustomException,
)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_quiz(request, course_slug: str, quiz_slug: str):
    # TODO: validations

    user_id = request.user.id
    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN,
        )
    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    quiz.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
