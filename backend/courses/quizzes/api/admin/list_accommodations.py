from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import QuizAccommodationListItemSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["GET"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def list_quiz_accommodations(request, course_slug: str, quiz_slug: str):
    accommodations = db.QuizAccommodation.objects.filter(quiz=request.quiz)

    serializer = QuizAccommodationListItemSerializer(
        accommodations,
        many=True,
    )

    return Response(
        status=status.HTTP_200_OK, data={"quiz_accommodations": serializer.data}
    )
