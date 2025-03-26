from rest_framework import serializers
import courses.models as db
from datetime import datetime
from django.contrib.auth.models import User


class CreateQuizRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)

    visible_at_timestamp = serializers.IntegerField(required=True)
    releases_at_timestamp = serializers.IntegerField(
        required=True
    )
    starts_at_timestamp = serializers.IntegerField(
        required=True
    )  # TODO: validate ends_at > starts_at
    ends_at_timestamp = serializers.IntegerField(required=True)

    github_repository = serializers.CharField(required=True)


class EditQuizRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)

    visible_at_timestamp = serializers.IntegerField(required=False)
    starts_at_timestamp = serializers.IntegerField(
        required=False
    )  # TODO: validate ends_at > starts_at
    ends_at_timestamp = serializers.IntegerField(required=False)

    github_repository = serializers.CharField(required=False)


class UnixTimestampDateTimeField(serializers.DateTimeField):
    """
    A custom field that accepts/outputs Unix timestamps.
    """

    def to_internal_value(self, value: int):
        """
        Parse the incoming integer timestamp and convert to a datetime.
        """
        local_tz = datetime.now().astimezone().tzinfo
        dt = datetime.fromtimestamp(int(value), tz=local_tz)

        return dt


class QuizAccommodationSerializer(serializers.ModelSerializer):
    visible_at = UnixTimestampDateTimeField()
    starts_at = UnixTimestampDateTimeField()
    ends_at = UnixTimestampDateTimeField()

    username = serializers.SlugRelatedField(
        source="user",
        slug_field="username",
        queryset=User.objects.all(),
        error_messages={
            "does_not_exist": "The username you entered does not exist",
            "invalid": "Invalid username format",
        },
    )

    class Meta:
        model = db.QuizAccommodation
        fields = ["username", "quiz", "visible_at", "starts_at", "ends_at"]


class QuizAccommodationListItemSerializer(serializers.ModelSerializer):
    visible_at_unix_timestamp = serializers.SerializerMethodField()
    starts_at_unix_timestamp = serializers.SerializerMethodField()
    ends_at_unix_timestamp = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username")

    class Meta:
        model = db.QuizAccommodation
        fields = [
            "user_id",
            "username",
            "visible_at_unix_timestamp",
            "starts_at_unix_timestamp",
            "ends_at_unix_timestamp",
        ]

    def get_ends_at_unix_timestamp(self, quiz: db.Quiz) -> int:
        return int(quiz.ends_at.timestamp())

    def get_starts_at_unix_timestamp(self, quiz: db.Quiz) -> int:
        return int(quiz.starts_at.timestamp())

    def get_visible_at_unix_timestamp(self, quiz: db.Quiz) -> int:
        return int(quiz.visible_at.timestamp())


class EditQuizSerializer(serializers.ModelSerializer):
    releases_at = UnixTimestampDateTimeField()
    visible_at = UnixTimestampDateTimeField()
    starts_at = UnixTimestampDateTimeField()
    ends_at = UnixTimestampDateTimeField()

    class Meta:
        model = db.Quiz
        fields = ["slug", "title", "visible_at", "starts_at", "ends_at", "releases_at"]


class DeleteQuizAccommodationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)


class BaseQuestionSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True)
    points = serializers.IntegerField(required=True, min_value=0)
    order = serializers.IntegerField(required=True)


BASE_QUESTION_FIELDS = ["prompt", "render_prompt_as_latex", "points", "order"]


class MultipleChoiceQuestionRequestSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(), min_length=1, required=True
    )

    class Meta:
        model = db.MultipleChoiceQuestion
        fields = BASE_QUESTION_FIELDS + ["options", "correct_option_index"]


class CheckboxQuestionRequestSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(), min_length=1, required=True
    )
    correct_option_indices = serializers.ListField(
        child=serializers.IntegerField(min_value=0), required=True
    )

    class Meta:
        model = db.CheckboxQuestion
        fields = BASE_QUESTION_FIELDS + ["options", "correct_option_indices"]


class WrittenResponseQuestionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = db.WrittenResponseQuestion
        fields = BASE_QUESTION_FIELDS + ["max_length"]


class CodingQuestionRequestSerializer(serializers.ModelSerializer):
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
