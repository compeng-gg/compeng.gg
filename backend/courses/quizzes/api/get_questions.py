from courses.quizzes.api.utils import get_quiz_images_from_question_list, get_quiz_questions
import courses.models as db
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch, prefetch_related_objects
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import QuizSerializer
from django.utils import timezone
from typing import Union


def get_quiz_or_error_response(
    user_id: int, course_slug: str, quiz_slug: str
) -> Union[db.Quiz, Response]:
    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        db.Enrollment.objects.get(
            role__kind=db.Role.Kind.STUDENT,
            role__offering=quiz.offering,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise ValidationError("Student is not enrolled in this course")

    if quiz.starts_at > timezone.now():
        return Response(
            {"error": "Quiz has not started yet"}, status=status.HTTP_403_FORBIDDEN
        )

    return quiz


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_questions(request, course_slug: str, quiz_slug: str):
    request_at = timezone.now()

    user_id = request.user.id

    quiz_or_error_response = get_quiz_or_error_response(user_id, course_slug, quiz_slug)

    if isinstance(quiz_or_error_response, Response):
        error_response = quiz_or_error_response
        return error_response

    quiz = quiz_or_error_response

    if quiz is None:
        return Response(
            data={"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND
        )

    written_response_questions_prefetch = Prefetch(
        "written_response_questions",
        queryset=db.WrittenResponseQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.WrittenResponseAnswer.objects.filter(
                    quiz_submission__user_id=user_id
                ),
            )
        ),
    )

    coding_questions_prefetch = Prefetch(
        "coding_questions",
        queryset=db.CodingQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.CodingAnswer.objects.filter(
                    quiz_submission__user_id=user_id
                ),
            )
        ),
    )

    multiple_choice_questions_prefetch = Prefetch(
        "multiple_choice_questions",
        queryset=db.MultipleChoiceQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.MultipleChoiceAnswer.objects.filter(
                    quiz_submission__user_id=user_id
                ),
            )
        ),
    )

    checkbox_questions_prefetch = Prefetch(
        "checkbox_questions",
        queryset=db.CheckboxQuestion.objects.prefetch_related(
            Prefetch(
                "answers",
                queryset=db.CheckboxAnswer.objects.filter(
                    quiz_submission__user_id=user_id
                ),
            )
        ),
    )

    prefetch_related_objects(
        [quiz],
        written_response_questions_prefetch,
        coding_questions_prefetch,
        multiple_choice_questions_prefetch,
        checkbox_questions_prefetch,
    )
    
    quiz_questions = get_quiz_questions(quiz)
    quiz.images = get_quiz_images_from_question_list(quiz_questions)

    with transaction.atomic():
        try:
            quiz_submission = db.QuizSubmission.objects.get(
                quiz=quiz,
                user_id=user_id,
            )

            if (
                not quiz.content_viewable_after_submission
                and quiz_submission.completed_at <= timezone.now()
            ):
                return Response(
                    {"error": "Quiz content cannot be viewed after submission"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except db.QuizSubmission.DoesNotExist:
            db.QuizSubmission.objects.create(
                user_id=user_id,
                quiz=quiz,
                started_at=request_at,
                completed_at=quiz.ends_at,  # Initialize this to the end datetime for the quiz
            )

    return Response(data=QuizSerializer(quiz).data)
