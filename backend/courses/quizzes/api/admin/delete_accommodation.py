from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.schema import DeleteQuizAccommodationSerializer
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["DELETE"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def delete_quiz_accommodation(request, course_slug: str, quiz_slug: str):
    serializer = DeleteQuizAccommodationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        quiz_accommodation = db.QuizAccommodation.objects.get(
            quiz=request.quiz,
            user__username=serializer.validated_data["username"],
        )
    except db.QuizAccommodation.DoesNotExist:
        return Response(
            {"error": "Quiz accommodation does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    quiz_accommodation.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
