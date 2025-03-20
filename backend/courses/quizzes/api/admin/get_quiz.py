from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
import courses.models as db
from django.forms.models import model_to_dict
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


@api_view(["GET"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def get_quiz(request, course_slug: str, quiz_slug: str):
    quiz = request.quiz
    quiz_data = model_to_dict(quiz)

    quiz_data["starts_at"] = int(quiz_data["starts_at"].timestamp())
    quiz_data["ends_at"] = int(quiz_data["ends_at"].timestamp())
    quiz_data["visible_at"] = int(quiz_data["visible_at"].timestamp())

    quiz_data.pop("repository")

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
            data.pop("images")

            questions.append(data)

    questions = sorted(questions, key=lambda x: x["order"])

    quiz_data["questions"] = questions
    quiz_data["github_repository"] = quiz.repository.full_name

    return Response(status=status.HTTP_200_OK, data=quiz_data)
