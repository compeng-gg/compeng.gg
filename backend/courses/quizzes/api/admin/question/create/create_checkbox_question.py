from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import CheckboxQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.utils import (
    validate_user_is_ta_or_instructor_in_course,
    CustomException,
)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_checkbox_question(request, course_slug: str, quiz_slug: str):
    serializer = CheckboxQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id

    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    options = serializer.validated_data.get("options")
    correct_option_indices = serializer.validated_data.get("correct_option_indices")

    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)

    checkbox_question = db.CheckboxQuestion.objects.create(
        prompt=prompt,
        points=points,
        order=order,
        options=options,
        correct_option_indices=correct_option_indices,
        quiz=quiz,
    )

    return Response(
        status=status.HTTP_200_OK, data={"question_id": checkbox_question.id}
    )
