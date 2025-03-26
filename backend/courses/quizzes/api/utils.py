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
    if type == "multiple_choice" :
        return db.MultipleChoiceQuestion.objects.get(id=id)
    if type == "checkbox":
        return db.CheckboxQuestion.objects.get(id=id)
    if type == "coding":
        return db.CodingQuestion.objects.get(id=id)
    if type == "written_response":
        return db.WrittenResponseQuestion.objects.get(id=id)
    return None
