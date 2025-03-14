from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import (
    MultipleChoiceQuestionRequestSerializer,
)
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_multiple_choice_question(request, course_slug: str, quiz_slug: str):
    serializer = MultipleChoiceQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    options = serializer.validated_data.get("options")
    correct_option_index = serializer.validated_data.get("correct_option_index")
    render_prompt_as_latex = serializer.validated_data.get("render_prompt_as_latex")

    multiple_choice_question = db.MultipleChoiceQuestion.objects.create(
        prompt=prompt,
        render_prompt_as_latex=render_prompt_as_latex,
        points=points,
        order=order,
        options=options,
        correct_option_index=correct_option_index,
        quiz=request.quiz,
    )

    return Response(
        status=status.HTTP_200_OK, data={"question_id": multiple_choice_question.id}
    )
