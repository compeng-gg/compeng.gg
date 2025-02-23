from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from uuid import UUID
import courses.models as db


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_checkbox_question(
    request, course_slug: str, quiz_slug: str, checkbox_question_id: UUID
):
    # TODO: validations
    checkbox_question = db.CheckboxQuestion.objects.get(id=checkbox_question_id)
    checkbox_question.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_multiple_choice_question(
    request, course_slug: str, quiz_slug: str, multiple_choice_question_id: UUID
):
    # TODO: validations
    multiple_choice_question = db.MultipleChoiceQuestion.objects.get(
        id=multiple_choice_question_id
    )
    multiple_choice_question.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_coding_question(
    request, course_slug: str, quiz_slug: str, coding_question_id: UUID
):
    # TODO: validations
    coding_question = db.CodingQuestion.objects.get(id=coding_question_id)
    coding_question.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_written_response_question(
    request, course_slug: str, quiz_slug: str, written_response_question_id: UUID
):
    # TODO: validations
    written_response_question = db.WrittenResponseQuestion.objects.get(
        id=written_response_question_id
    )
    written_response_question.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
