from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
import courses.models as db
from django.forms.models import model_to_dict


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def admin_list_quizzes_for_course(request, course_slug: str):
    # TODO: validations
    # TODO: Exclude quizzes from dead offerings. Or just include the offering slug in URLs
    quizzes = db.Quiz.objects.filter(offering__course__slug=course_slug).all()


    quizzes_list = []

    for quiz in quizzes:
        quiz_data = model_to_dict(quiz)
        data = {
            "title": quiz_data["title"],
            "slug": quiz_data["slug"],
            "visible_at": int(quiz_data["visible_at"].timestamp()),
            "starts_at": int(quiz_data["starts_at"].timestamp()),
            "ends_at": int(quiz_data["ends_at"].timestamp())
        }

        quizzes_list.append(data)

    response_data = {
        "quizzes": quizzes_list
    }

    return Response(status=status.HTTP_200_OK, data=response_data)
