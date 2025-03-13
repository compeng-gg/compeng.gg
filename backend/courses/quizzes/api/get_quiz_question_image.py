import courses.models as db
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from uuid import UUID
from django.shortcuts import get_object_or_404
from django.http import FileResponse


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_quiz_question_image(
    request, course_slug: str, quiz_slug: str, question_image_id: UUID
):
    # TODO extra validations
    quiz_image = get_object_or_404(db.QuizQuestionImage, id=question_image_id)
    return FileResponse(quiz_image.image.open(), content_type="image/jpeg")
