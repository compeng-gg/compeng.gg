from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["DELETE"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def delete_quiz(request, course_slug: str, quiz_slug: str):
    request.quiz.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
