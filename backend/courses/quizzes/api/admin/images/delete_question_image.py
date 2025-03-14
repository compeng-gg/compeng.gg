from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["DELETE"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def delete_question_image(request, course_slug: str, quiz_slug: str, image_id: str):
    # TODO validate that the image belongs to the quiz

    questionImage = db.QuizQuestionImage.objects.get(id=image_id)
    questionImage.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
