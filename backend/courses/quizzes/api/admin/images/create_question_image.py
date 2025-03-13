from courses.quizzes.api.admin.utils import validate_user_is_ta_or_instructor_in_course
from courses.quizzes.api.utils import get_question_from_id_and_type
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from courses.quizzes.api.admin.images.schema import CreateQuestionImageRequestSerializer
from rest_framework.response import Response
import courses.models as db
from django.contrib.contenttypes.models import ContentType


class CustomException(Exception):
    pass

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_question_image(request, course_slug: str, quiz_slug: str):
    serializer = CreateQuestionImageRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = request.user.id
    try:
        validate_user_is_ta_or_instructor_in_course(user_id, course_slug)
    except CustomException as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN,
        )
        
    question_id = serializer.validated_data.get("question_id")
    question_type = serializer.validated_data.get("question_type")
    
    #Validate that the question exists
    question = get_question_from_id_and_type(question_id, question_type)
    if question == None:
        return Response(
            {"error": "Question not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    caption = serializer.caption
    image = serializer.image
    
    db.QuestionImage.objects.create(
        question=question,
        caption=caption,
        image=image
    )

    

