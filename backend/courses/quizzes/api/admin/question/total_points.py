import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from typing import Optional, Union, Type
from django.utils import timezone
from django.forms.models import model_to_dict
from django.db.models import Sum

def update_quiz_total_points(course_slug, quiz_slug):
    """
    Updates the total_points field in the Quiz model by summing up all question points.
    """
    # Fetch the quiz
    quiz = db.Quiz.objects.get(slug=quiz_slug, offering__course__slug=course_slug)

    # Compute total points by summing up the 'points' field from all question types
    total_points = (
        db.WrittenResponseQuestion.objects.filter(quiz=quiz).aggregate(Sum("points"))["points__sum"] or 0
    ) + (
        db.CodingQuestion.objects.filter(quiz=quiz).aggregate(Sum("points"))["points__sum"] or 0
    ) + (
        db.MultipleChoiceQuestion.objects.filter(quiz=quiz).aggregate(Sum("points"))["points__sum"] or 0
    ) + (
        db.CheckboxQuestion.objects.filter(quiz=quiz).aggregate(Sum("points"))["points__sum"] or 0
    )

    # Update and save the total points in the quiz
    quiz.total_points = total_points
    quiz.save()