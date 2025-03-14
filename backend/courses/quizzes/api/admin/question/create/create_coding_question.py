from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import CodingQuestionRequestSerializer
from rest_framework.response import Response
import courses.models as db
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_coding_question(request, course_slug: str, quiz_slug: str):
    serializer = CodingQuestionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    prompt = serializer.validated_data.get("prompt")
    points = serializer.validated_data.get("points")
    order = serializer.validated_data.get("order")
    starter_code = serializer.validated_data.get("starter_code")
    programming_language = serializer.validated_data.get("programming_language")
    files = serializer.validated_data.get("files")
    file_to_replace = serializer.validated_data.get("file_to_replace")
    grading_file_directory = serializer.validated_data.get("grading_file_directory")

    coding_question = db.CodingQuestion.objects.create(
        prompt=prompt,
        points=points,
        order=order,
        starter_code=starter_code,
        programming_language=programming_language,
        files=files,
        file_to_replace=file_to_replace,
        grading_file_directory=grading_file_directory,
        quiz=request.quiz,
    )

    return Response(status=status.HTTP_200_OK, data={"question_id": coding_question.id})
