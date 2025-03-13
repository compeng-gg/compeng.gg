from rest_framework import serializers
import courses.models as db

class CreateQuestionImageRequestSerializer(serializers.Serializer):
    question_id = serializers.CharField(required=True)
    question_type = serializers.ChoiceField(choices = db.QuestionType.choices)
    image = serializers.ImageField(required=True)
    caption = serializers.CharField()
    
    def validate_image(self, value):
        max_size = 5 * 1024 * 1024  # 5MB limit

        if value.size > max_size:
            raise serializers.ValidationError("Image size should not exceed 5MB. Image size is " + str(value.size) + " bytes")
        
        return value

class DeleteQuestionImageRequestSerializer(serializers.Serializer):
    question_id = serializers.CharField(required=True)
    question_type = serializers.ChoiceField(choices = db.QuestionType.choices)
    image_id = serializers.CharField(required=True)
