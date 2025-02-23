import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from typing import Optional, Union, Type
from django.utils import timezone


def get_existing_answer_object(
    answer_model: Union[
        Type[db.MultipleChoiceAnswer],
        Type[db.CheckboxAnswer],
        Type[db.CodingAnswer],
        Type[db.WrittenResponseAnswer],
    ],
    question_id: UUID,
    user_id: int,
) -> Optional[
    Union[
        db.MultipleChoiceAnswer,
        db.CheckboxAnswer,
        db.CodingAnswer,
        db.WrittenResponseAnswer,
    ]
]:
    try:
        answer_object = answer_model.objects.get(
            question_id=question_id, quiz_submission__user_id=user_id
        )
        return answer_object
    except answer_model.DoesNotExist:
        return None


def get_quiz_submission_or_error_response(
    request_at: datetime, user_id: int, course_slug: str, quiz_slug: str
) -> Union[db.QuizSubmission, Response]:
    quiz_or_error_response = get_quiz_or_error_response(
        user_id=user_id, course_slug=course_slug, quiz_slug=quiz_slug
    )

    if isinstance(quiz_or_error_response, Response):
        error_response = quiz_or_error_response
        return error_response

    quiz = quiz_or_error_response

    try:
        quiz_submission = db.QuizSubmission.objects.get(
            quiz=quiz,
            user_id=user_id,
        )
    except db.QuizSubmission.DoesNotExist:
        return Response(
            {"error": "Quiz submission not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request_at > quiz_submission.completed_at:
        return Response(
            {"error": "The quiz has already been completed"},
            status=status.HTTP_403_FORBIDDEN,
        )

    return quiz_submission


def get_quiz_or_error_response(
    user_id: int, course_slug: str, quiz_slug: str
) -> db.Quiz:
    try:
        db.Enrollment.objects.get(
            role__kind=db.Role.Kind.STUDENT,
            role__offering__course__slug=course_slug,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        return Response(
            {"error": "Student is not enrolled in this course"},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        quiz = db.Quiz.objects.get(offering__course__slug=course_slug, slug=quiz_slug)
    except db.Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    if quiz.starts_at > timezone.now():
        return Response(
            {"error": "Quiz has not started yet"}, status=status.HTTP_403_FORBIDDEN
        )

    return quiz
