from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import CreateCheckboxQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def edit_checkbox_question(
    request, course_slug: str, quiz_slug: str, checkbox_question_id: str
):
    # TODO: validate user is instructor or TA in course
    # TODO: validate quiz matches question
    checkbox_question = db.CheckboxQuestion.objects.get(id=checkbox_question_id)
    serializer = CreateCheckboxQuestionRequestSerializer(
        checkbox_question, data=request.data, partial=True
    )
    print(request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    print(serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)
