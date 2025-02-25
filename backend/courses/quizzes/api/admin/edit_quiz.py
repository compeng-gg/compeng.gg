from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.schema import EditQuizSerializer


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def edit_quiz(request, course_slug: str, quiz_slug: str):
    # TODO: validations
    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)


    serializer = EditQuizSerializer(quiz, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    
    
    return Response(status=status.HTTP_204_NO_CONTENT)
