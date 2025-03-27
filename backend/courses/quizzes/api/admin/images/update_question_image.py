from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.images.schema import UpdateQuestionImageRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def update_question_image(request, course_slug: str, quiz_slug: str, image_id: str):
    question_image = db.QuizQuestionImage.objects.get(id=image_id)
    serializer = UpdateQuestionImageRequestSerializer(question_image, data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
