from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import QuizAccommodationSerializer
from rest_framework.response import Response
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_quiz_accommodation(request, course_slug: str, quiz_slug: str):
    data = request.data.copy()
    data["quiz"] = request.quiz.id

    serializer = QuizAccommodationSerializer(data=data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(
        status=status.HTTP_200_OK, data={"accommodation_id": serializer.instance.id}
    )
