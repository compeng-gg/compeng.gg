from datetime import datetime
import courses.models as db
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA

@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def compute_total_grade(request, quiz_slug, student_id,):
    """
    Compute the total grade for a student's quiz submission by summing up all question grades.
    """
    try:
        submission = db.QuizSubmission.objects.get(
            quiz__slug=quiz_slug, user_id=student_id
        )
    except db.QuizSubmission.DoesNotExist:
        return 


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


    submission.grade = total_grade
    submission.graded_by = request.user
    submission.graded_at = datetime.now()
    submission.save()
    
    return Response({"message": "Total grade computed successfully"}, status=status.HTTP_200_OK)


import json 


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def update_submission_question(request, quiz_slug, student_id):
    """
    Update the grade and comment for a specific question answer in a submission.
    """

    print(
        "Incoming Request Data:", json.dumps(request.data, indent=4)
    ) 

    try:
        submission = db.QuizSubmission.objects.get(
            quiz__slug=quiz_slug, user_id=student_id
        )
    except db.QuizSubmission.DoesNotExist:
        return Response(
            {"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND
        )

    data = request.data
    question_id = data.get("question_id") 
    grade = data.get("grade")
    comment = data.get("comment", "")

    if not question_id:
        return Response(
            {"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )


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
            break 
        except model.DoesNotExist:
            continue 

    if answer is None:
        return Response({"error": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)


    if grade is not None:
        try:
            grade = int(grade)
        except ValueError:
            return Response(
                {"error": "Invalid grade format"}, status=status.HTTP_400_BAD_REQUEST
            )


    answer.grade = grade
    answer.comment = comment
    answer.save()

    # compute_total_grade(request, course_slug, quiz_slug, student_id)
    print("Updated Answer:", answer)

    return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
