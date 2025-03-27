from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from courses.quizzes.api.admin.schema import EditQuizSerializer
from datetime import timezone
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def edit_quiz(request, course_slug: str, quiz_slug: str):
    serializer = EditQuizSerializer(request.quiz, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def release_quiz_now(request, course_slug: str, quiz_slug: str):
    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    quiz.release_answers_at = timezone.now()
    return Response(status=status.HTTP_204_NO_CONTENT)
