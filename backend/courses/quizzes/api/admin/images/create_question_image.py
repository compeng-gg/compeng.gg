from courses.quizzes.api.utils import get_question_from_id_and_type
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.images.schema import CreateQuestionImageRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


class CustomException(Exception):
    pass


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_question_image(request, course_slug: str, quiz_slug: str):
    serializer = CreateQuestionImageRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question_id = serializer.validated_data.get("question_id")
    question_type = serializer.validated_data.get("question_type")

    # Validate that the question exists
    question = get_question_from_id_and_type(question_id, question_type)
    if question == None:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    image = serializer.image
    order = serializer.order
    caption = serializer.caption

    db.QuizQuestionImage.objects.create(image=image, order=order, caption=caption)

    return Response(status=status.HTTP_201_CREATED)
