import courses.models as db
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from courses.quizzes.schemas import QuizSerializer
from django.db.models import Prefetch

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_quiz_submissions(request, course_slug: str, quiz_slug: str):
    """
    Retrieve all quiz submissions for a given quiz.
    """

    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure user has instructor or TA role
    user_id = request.user.id
    if not db.Enrollment.objects.filter(
        user_id=user_id, role__offering=quiz.offering, role__kind__in=[db.Role.Kind.INSTRUCTOR, db.Role.Kind.TA]
    ).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Fetch quiz submissions along with user and grader data
    quiz_submissions = db.QuizSubmission.objects.filter(quiz=quiz).select_related("user", "graded_by")

    # Serialize the data
    submission_data = [
        {
            "user_id": submission.user.id,
            "username": submission.user.username,
            "started_at": submission.started_at,
            "completed_at": submission.completed_at,
            "grade": submission.grade,  # Include grade
            "graded_at": submission.graded_at,  # Include grading timestamp
            "graded_by": submission.graded_by.username if submission.graded_by else None,  # Include grader username
        }
        for submission in quiz_submissions
    ]

    return Response(
        data={"total_points": quiz.total_points, "submissions": submission_data},  # Include total points
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_student_quiz_submission(request, course_slug: str, quiz_slug: str, student_id: int):
    """
    Retrieve a specific student's quiz submission along with all answers.
    """

    try:
        quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)
    except db.Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    # Ensure user is an instructor or TA
    user_id = request.user.id
    if not db.Enrollment.objects.filter(
        user_id=user_id, role__offering=quiz.offering, role__kind__in=[db.Role.Kind.INSTRUCTOR, db.Role.Kind.TA]
    ).exists():
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    # Get the student's quiz submission
    try:
        submission = db.QuizSubmission.objects.get(quiz=quiz, user_id=student_id)
    except db.QuizSubmission.DoesNotExist:
        return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

    # Prefetch answers for all question types
    multiple_choice_answers = db.MultipleChoiceAnswer.objects.filter(quiz_submission=submission).select_related("question")
    checkbox_answers = db.CheckboxAnswer.objects.filter(quiz_submission=submission).select_related("question")
    coding_answers = db.CodingAnswer.objects.filter(quiz_submission=submission).select_related("question")
    written_response_answers = db.WrittenResponseAnswer.objects.filter(quiz_submission=submission).select_related("question")

    # ✅ Modify serialized data to include per-question grade
    answer_data = {
        "multiple_choice_answers": [
            {
                "question": answer.question.prompt,
                "selected_answer_index": answer.selected_answer_index,
                "grade": answer.grade  # ✅ Include per-question grade
            }
            for answer in multiple_choice_answers
        ],
        "checkbox_answers": [
            {
                "question": answer.question.prompt,
                "selected_answer_indices": answer.selected_answer_indices,
                "grade": answer.grade  # ✅ Include per-question grade
            }
            for answer in checkbox_answers
        ],
        "coding_answers": [
            {
                "question": answer.question.prompt,
                "solution": answer.solution,
                "executions": list(answer.executions.values("solution", "result", "stderr", "status")),  # ✅ Include executions
                "grade": answer.grade  # ✅ Include per-question grade
            }
            for answer in coding_answers
        ],
        "written_response_answers": [
            {
                "question": answer.question.prompt,
                "response": answer.response,
                "grade": answer.grade  # ✅ Include per-question grade
            }
            for answer in written_response_answers
        ],
    }

    # Compile submission response
    submission_data = {
        "user_id": submission.user.id,
        "username": submission.user.username,
        "started_at": submission.started_at,
        "completed_at": submission.completed_at,
        "grade": submission.grade,  # ✅ Overall quiz grade
        "graded_at": submission.graded_at,
        "graded_by": submission.graded_by.username if submission.graded_by else None,
        "total_points": quiz.total_points,  # ✅ Include total points for the quiz
        "answers": answer_data
    }

    return Response(data=submission_data, status=status.HTTP_200_OK)
