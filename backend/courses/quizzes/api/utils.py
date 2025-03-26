import courses.models as db
from uuid import UUID
from typing import Optional, Union, Type


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


def get_question_from_id_and_type(id: str, type: str):
    type = type.lower()
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
    
