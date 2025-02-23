from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import CreateCodingQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.utils import (
    validate_user_is_ta_or_instructor_in_course,
    CustomException,
)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_coding_question(request, course_slug: str, quiz_slug: str):
    print(request.data)
    serializer = CreateCodingQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id

    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    print(serializer.validated_data)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    starter_code = serializer.validated_data.get("starter_code")
    programming_language = serializer.validated_data.get("programming_language")
    files = serializer.validated_data.get("files")
    file_to_replace = serializer.validated_data.get("file_to_replace")
    grading_file_directory = serializer.validated_data.get("grading_file_directory")

    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)

    print(programming_language)

    coding_question = db.CodingQuestion.objects.create(
        prompt=prompt,
        points=points,
        order=order,
        starter_code=starter_code,
        programming_language=programming_language,
        files=files,
        file_to_replace=file_to_replace,
        grading_file_directory=grading_file_directory,
        quiz=quiz,
    )

    return Response(status=status.HTTP_200_OK, data={"question_id": coding_question.id})
