import courses.models as db
from uuid import UUID
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from typing import Optional, Union, Type
from django.utils import timezone
from django.forms.models import model_to_dict

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

def get_question_from_id_and_type(id: str, type: str):
    if type == "multiple_choice":
        return db.MultipleChoiceQuestion.objects.get(id=id)
    if type == "checkbox":
        return db.CheckboxQuestion.objects.get(id=id)
    if type == "coding":
        return db.CodingQuestion.objects.get(id=id)
    if type == "written_response":
        return db.WrittenResponseQuestion.objects.get(id=id)
    return None

def get_quiz_questions(quiz):
    checkbox_questions = db.CheckboxQuestion.objects.filter(quiz=quiz).all()
    coding_questions = db.CodingQuestion.objects.filter(quiz=quiz).all()
    multiple_choice_questions = db.MultipleChoiceQuestion.objects.filter(
        quiz=quiz
    ).all()
    written_response_questions = db.WrittenResponseQuestion.objects.filter(
        quiz=quiz
    ).all()

    question_types = [
        ("CODING", coding_questions),
        ("MULTIPLE_CHOICE", multiple_choice_questions),
        ("WRITTEN_RESPONSE", written_response_questions),
        ("CHECKBOX", checkbox_questions),
    ]

    questions = []

    for question_type_key, question_type in question_types:
        for question in question_type:
            data = model_to_dict(question)
            data["question_type"] = question_type_key
            data["id"] = question.id
            data.pop("quiz")

            questions.append(data)

    questions = sorted(questions, key=lambda x: x["order"])

    return questions

def get_question_images(question):
    return db.QuestionImage.objects.filter(question_id=question.get("id"), question_type = question.get("question_type")).all()

#returns image urls for questions
#Returns a list of images for a quiz
def get_quiz_images_from_question_list(questions):
    images = []
    for question in questions:
        found_images = get_question_images(question)
        ret_val = []
        for image in found_images:
            ret_val.append(image.image.url)
        images.append(ret_val)
    return images
    
    