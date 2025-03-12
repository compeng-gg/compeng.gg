from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.schema import DeleteQuizAccommodationSerializer


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_quiz_accommodation(request, course_slug: str, quiz_slug: str):

    serializer = DeleteQuizAccommodationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response(
            {"error": "Quiz does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    try:
        quiz_accommodation = db.QuizAccommodation.objects.get(
            quiz=quiz,
            user__username=serializer.validated_data["username"],
        )
    except db.QuizAccommodation.DoesNotExist:
        return Response(
            {"error": "Quiz accommodation does not exist"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    quiz_accommodation.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
