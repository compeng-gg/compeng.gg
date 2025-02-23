from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.schema import CreateQuizRequestSerializer
from rest_framework.response import Response
from rest_framework import status
import courses.models as db
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
import requests
from datetime import datetime


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_quiz(request, course_slug: str, quiz_slug: str):
    # TODO: validations
    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    quiz.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
