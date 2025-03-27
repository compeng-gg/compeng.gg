from courses.quizzes.api.utils import get_question_from_id_and_type
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.images.schema import CreateQuestionImageRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_question_image(request, course_slug: str, quiz_slug: str):
    # Explicitly include request.FILES for file uploads
    serializer = CreateQuestionImageRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    question_id = serializer.validated_data.get("question_id")
    question_type = serializer.validated_data.get("question_type")
    caption = serializer.validated_data.get("caption")
    order = serializer.validated_data.get("order")
    image = serializer.validated_data.get("image")  # This is where your file is

    # Validate that the question exists
    question = get_question_from_id_and_type(question_id, question_type)
    if question is None:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    image = db.QuizQuestionImage.objects.create(
        image=image,
        order=order,
        caption=caption,
        quiz=question.quiz,  # you might want to associate this image with the question
    )

    question.images.add(image)

    return Response(status=status.HTTP_201_CREATED)
