import courses.models as db
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum


def compute_total_grade(course_slug: str, quiz_slug: str, student_id: int):
    """
    Compute the total grade for a student's quiz submission by summing up all question grades.
    """
    try:
        submission = db.QuizSubmission.objects.get(
            quiz__slug=quiz_slug, user_id=student_id
        )
    except db.QuizSubmission.DoesNotExist:
        return  # If no submission exists, do nothing

    # Get all answer models and their grades
    answer_models = [
        db.MultipleChoiceAnswer,
        db.CheckboxAnswer,
        db.CodingAnswer,
        db.WrittenResponseAnswer,
    ]

    total_grade = 0
    for model in answer_models:
        total_grade += (
            model.objects.filter(quiz_submission=submission)
            .exclude(grade=None)
            .aggregate(total=Sum("grade"))["total"]
            or 0
        )

    # ✅ Update the submission's total grade
    submission.grade = total_grade
    submission.save()


import json  # Add this at the top


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def update_submission_question(request, course_slug, quiz_slug, student_id):
    """
    Update the grade and comment for a specific question answer in a submission.
    """

    print(
        "Incoming Request Data:", json.dumps(request.data, indent=4)
    )  # ✅ Log request data

    try:
        submission = db.QuizSubmission.objects.get(
            quiz__slug=quiz_slug, user_id=student_id
        )
    except db.QuizSubmission.DoesNotExist:
        return Response(
            {"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data
    question_id = data.get("question_id")  # ✅ Ensure we're receiving the question ID
    grade = data.get("grade")
    comment = data.get("comment", "")

    if not question_id:
        return Response(
            {"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ Find the correct model dynamically using `question_id`
    answer_models = [
        db.MultipleChoiceAnswer,
        db.CheckboxAnswer,
        db.CodingAnswer,
        db.WrittenResponseAnswer,
    ]

    answer = None
    for model in answer_models:
        try:
            answer = model.objects.get(
                question_id=question_id, quiz_submission=submission
            )
            break  # ✅ Found the correct answer, exit the loop
        except model.DoesNotExist:
            continue  # ✅ Keep looking

    if answer is None:
        return Response({"error": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Ensure grade is an integer
    if grade is not None:
        try:
            grade = int(grade)
        except ValueError:
            return Response(
                {"error": "Invalid grade format"}, status=status.HTTP_400_BAD_REQUEST
            )

    # ✅ Update grade and comment
    answer.grade = grade
    answer.comment = comment
    answer.save()

    # ✅ Recalculate total grade
    compute_total_grade(course_slug, quiz_slug, student_id)

    return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
