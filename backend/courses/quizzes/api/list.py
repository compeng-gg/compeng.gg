import courses.models as db
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Subquery, Q
from courses.quizzes.schemas import (
    AllQuizzesListSerializer,
    CourseQuizzesListSerializer,
)
from typing import Optional


def query_quizzes(user_id: int, filter_params: Optional[Q] = Q()) -> QuerySet[db.Quiz]:
    return db.Quiz.objects.filter(
        Q(
            offering__in=Subquery(
                db.Enrollment.objects.filter(user_id=user_id).values_list(
                    "role__offering"
                )
            ),
            visible_at__lt=timezone.now(),
        )
        & filter_params
    ).order_by("starts_at", "-ends_at")


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_all(request) -> Response:
    user_id = request.user.id

    all_quizzes = query_quizzes(user_id=user_id)

    return Response(data=AllQuizzesListSerializer(all_quizzes, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_for_course(request, course_slug: str) -> Response:
    user_id = request.user.id

    filter_params = Q(offering__course__slug=course_slug)
    course_quizzes = query_quizzes(user_id=user_id, filter_params=filter_params)
    return Response(data=CourseQuizzesListSerializer(course_quizzes, many=True).data)
