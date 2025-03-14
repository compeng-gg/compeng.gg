from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import CheckboxQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def edit_checkbox_question(
    request, course_slug: str, quiz_slug: str, checkbox_question_id: str
):
    # TODO: validate quiz matches question
    checkbox_question = db.CheckboxQuestion.objects.get(id=checkbox_question_id)
    serializer = CheckboxQuestionRequestSerializer(
        checkbox_question, data=request.data, partial=True
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(status=status.HTTP_204_NO_CONTENT)
