import courses.models as db
from rest_framework.response import Response
from django.db.models import Prefetch, prefetch_related_objects
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from courses.quizzes.schemas import QuizSerializer
from django.utils import timezone
from courses.quizzes.api.permissions import StudentCanViewQuiz


@api_view(["GET"])
@permission_classes([StudentCanViewQuiz])
def get_questions(request, course_slug: str, quiz_slug: str):
    request_at = timezone.now()

    user_id = request.user.id
    quiz = request.quiz
    accommodation = request.accommodation

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

    with transaction.atomic():
        try:
            quiz_submission = db.QuizSubmission.objects.get(
                quiz=quiz,
                user_id=user_id,
            )
        except db.QuizSubmission.DoesNotExist:
            db.QuizSubmission.objects.create(
                user_id=user_id,
                quiz=quiz,
                started_at=request_at,
                completed_at=quiz.ends_at
                if accommodation is None
                else accommodation.ends_at,  # Initialize this to the end datetime for the quiz
            )

    return Response(data=QuizSerializer(quiz).data)
