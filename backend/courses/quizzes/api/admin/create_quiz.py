from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from courses.quizzes.api.admin.schema import CreateQuizRequestSerializer
from rest_framework.response import Response
import courses.models as db
from django.contrib.contenttypes.models import ContentType
import requests
from datetime import datetime
from courses.quizzes.api.admin.permissions import IsAuthenticatedCourseInstructorOrTA


GITHUB_REPOS_API_BASE = "https://api.github.com/repos"


@api_view(["POST"])
@permission_classes([IsAuthenticatedCourseInstructorOrTA])
def create_quiz(request, course_slug: str):
    serializer = CreateQuizRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    title = serializer.validated_data.get("title")
    slug = serializer.validated_data.get("slug")
    visible_at_timestamp = serializer.validated_data.get("visible_at_timestamp")
    starts_at_timestamp = serializer.validated_data.get("starts_at_timestamp")
    ends_at_timestamp = serializer.validated_data.get("ends_at_timestamp")
    github_repository = serializer.validated_data.get("github_repository")

    offering = db.Offering.objects.get(course__slug=course_slug, active=True)

    if db.Quiz.objects.filter(slug=slug, offering=offering).exists():
        return Response(
            {"error": "Quiz slug already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    local_tz = datetime.now().astimezone().tzinfo

    visible_at = datetime.fromtimestamp(visible_at_timestamp, tz=local_tz)
    starts_at = datetime.fromtimestamp(starts_at_timestamp, tz=local_tz)
    ends_at = datetime.fromtimestamp(ends_at_timestamp, tz=local_tz)

    repo_api_url = f"{GITHUB_REPOS_API_BASE}/{github_repository}"
    github_repo_response = requests.get(repo_api_url)

    if github_repo_response.status_code == status.HTTP_404_NOT_FOUND:
        return Response(
            {"error": "GitHub repository not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if github_repo_response.status_code != status.HTTP_200_OK:
        return Response(
            {"error": "There was an error fetching the GitHub repository"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    github_repo_data = github_repo_response.json()

    github_repo_id = github_repo_data["id"]
    github_repo_name = github_repo_data["name"]
    github_repo_full_name = github_repo_data["full_name"]
    github_repo_owner_id = github_repo_data["owner"]["id"]

    owner_content_type = ContentType.objects.get_for_model(db.Quiz)

    repository, _ = db.Repository.objects.get_or_create(
        id=github_repo_id,
        defaults={
            "name": github_repo_name,
            "full_name": github_repo_full_name,
            "owner_id": github_repo_owner_id,
            "owner_content_type": owner_content_type,
        },
    )

    db.Quiz.objects.create(
        title=title,
        slug=slug,
        visible_at=visible_at,
        starts_at=starts_at,
        ends_at=ends_at,
        offering=offering,
        repository=repository,
    )

    return Response(status=status.HTTP_200_OK, data={})
