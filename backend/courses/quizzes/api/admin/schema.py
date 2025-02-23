from rest_framework import serializers
import courses.models as db


class CreateQuizRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)

    visible_at_timestamp = serializers.IntegerField(required=True)
    starts_at_timestamp = serializers.IntegerField(
        required=True
    )  # TODO: validate ends_at > starts_at
    ends_at_timestamp = serializers.IntegerField(required=True)

    github_repository = serializers.CharField(required=True)


class BaseCreateQuestionSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
    points = serializers.IntegerField(required=True, min_value=0)
    order = serializers.IntegerField(required=True)


BASE_QUESTION_FIELDS = ["prompt", "points", "order"]


class CreateMultipleChoiceQuestionRequestSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(), min_length=1, required=True
    )

    class Meta:
        model = db.MultipleChoiceQuestion
        fields = BASE_QUESTION_FIELDS + ["options", "correct_option_index"]


class CreateCheckboxQuestionRequestSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(), min_length=1, required=True
    )
    correct_option_indices = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=True
    )

    class Meta:
        model = db.CheckboxQuestion
        fields = BASE_QUESTION_FIELDS + ["options", "correct_option_indices"]


class CreateWrittenResponseQuestionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = db.WrittenResponseQuestion
        fields = BASE_QUESTION_FIELDS + ["max_length"]


class CreateCodingQuestionRequestSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.CharField(), min_length=1, required=True
    )

    class Meta:
        model = db.CodingQuestion
        fields = BASE_QUESTION_FIELDS + [
            "starter_code",
            "programming_language",
            "files",
            "file_to_replace",
            "grading_file_directory",
        ]
