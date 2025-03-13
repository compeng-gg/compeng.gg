from courses.quizzes.api.admin.utils import validate_user_is_ta_or_instructor_in_course
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.utils import CustomException


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_question_image(request, course_slug: str, quiz_slug: str, image_id: str):
    user_id = request.user.id
    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN,
        )

    # TODO validate that the image belongs to the quiz

    questionImage = db.QuizQuestionImage.objects.get(id=image_id)
    questionImage.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
