from tests.utils import (
    TestCasesWithUserAuth,
    create_enrollment,
    create_offering,
    create_repository,
    create_quiz,
)
import courses.models as db
import responses
from courses.quizzes.api.admin.create_quiz import GITHUB_REPOS_API_BASE
from rest_framework import status


class CreateQuizTests(TestCasesWithUserAuth):
    def get_api_endpoint(self, course_slug: str) -> str:
        return f"/api/v0/quizzes/admin/{course_slug}/create/"

    @responses.activate
    def test_happy_path__new_repo(self):
        mock_offering = create_offering()

        create_enrollment(
            user_id=self.user.id, offering=mock_offering, kind=db.Role.Kind.INSTRUCTOR
        )

        github_repository = "user_name/repo_name"
        github_repository_id = 1
        github_repo_name = "repo_name"
        github_repo_full_name = "user_name/repo_name"
        github_repo_owner_id = 1

        # Mock the response from GitHub API for repository metadata
        responses.add(
            responses.GET,
            f"{GITHUB_REPOS_API_BASE}/{github_repository}",
            json={
                "id": github_repository_id,
                "name": github_repo_name,
                "full_name": github_repo_full_name,
                "owner": {
                    "id": github_repo_owner_id,
                },
            },
            status=status.HTTP_200_OK,
        )

        quiz_slug = "quiz-slug"
        quiz_title = "Quiz Title"
        visible_at_timestamp = 1740248155
        starts_at_timestamp = 1740248155
        ends_at_timestamp = 1740248155

        request_data = {
            "title": quiz_title,
            "slug": quiz_slug,
            "visible_at_timestamp": visible_at_timestamp,
            "starts_at_timestamp": starts_at_timestamp,
            "ends_at_timestamp": ends_at_timestamp,
            "github_repository": github_repository,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        repository = db.Repository.objects.get(id=github_repository_id)

        # Validate repo details match the ones defined in the mocked response
        self.assertEqual(repository.name, github_repo_name)
        self.assertEqual(repository.full_name, github_repo_full_name)
        self.assertEqual(repository.owner_id, github_repo_owner_id)

        # Validate quiz creation
        self.assertEqual(db.Quiz.objects.count(), 1)

        quiz = db.Quiz.objects.get(slug=quiz_slug)

        self.assertEqual(quiz.title, quiz_title)
        self.assertEqual(quiz.repository, repository)
        self.assertEqual(quiz.visible_at.timestamp(), visible_at_timestamp)
        self.assertEqual(quiz.starts_at.timestamp(), starts_at_timestamp)
        self.assertEqual(quiz.ends_at.timestamp(), ends_at_timestamp)

    @responses.activate
    def test_happy_path__existing_repo(self):
        mock_offering = create_offering()
        mock_repository = create_repository()

        create_enrollment(
            user_id=self.user.id, offering=mock_offering, kind=db.Role.Kind.INSTRUCTOR
        )

        # Mock the response from GitHub API for repository metadata
        responses.add(
            responses.GET,
            f"{GITHUB_REPOS_API_BASE}/{mock_repository.full_name}",
            json={
                "id": mock_repository.id,
                "name": mock_repository.name,
                "full_name": mock_repository.full_name,
                "owner": {
                    "id": mock_repository.owner_id,
                },
            },
            status=status.HTTP_200_OK,
        )

        request_data = {
            "title": "Quiz Title",
            "slug": "quiz-slug",
            "visible_at_timestamp": 1740248155,
            "starts_at_timestamp": 1740248155,
            "ends_at_timestamp": 1740248155,
            "github_repository": mock_repository.full_name,
        }

        self.assertEqual(db.Repository.objects.count(), 1)

        response = self.client.post(
            self.get_api_endpoint(mock_offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(db.Repository.objects.count(), 1)

    @responses.activate
    def test_user_not_instructor_or_ta_throws_error(self):
        mock_offering = create_offering()
        mock_repository = create_repository()

        create_enrollment(
            user_id=self.user.id, offering=mock_offering, kind=db.Role.Kind.STUDENT
        )

        request_data = {
            "title": "Quiz Title",
            "slug": "quiz-slug",
            "visible_at_timestamp": 1740248155,
            "starts_at_timestamp": 1740248155,
            "ends_at_timestamp": 1740248155,
            "github_repository": mock_repository.full_name,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = response.json()
        expected_data = {"detail": "User is not a TA or Instructor in this course"}

        self.assertEqual(data, expected_data)

    @responses.activate
    def test_github_repo_not_found_throws_error(self):
        mock_offering = create_offering()
        mock_repository = create_repository()

        create_enrollment(
            user_id=self.user.id, offering=mock_offering, kind=db.Role.Kind.INSTRUCTOR
        )

        # Mock a 404 response from GitHub API for repository metadata
        responses.add(
            responses.GET,
            f"{GITHUB_REPOS_API_BASE}/{mock_repository.full_name}",
            status=status.HTTP_404_NOT_FOUND,
        )

        request_data = {
            "title": "Quiz Title",
            "slug": "quiz-slug",
            "visible_at_timestamp": 1740248155,
            "starts_at_timestamp": 1740248155,
            "ends_at_timestamp": 1740248155,
            "github_repository": mock_repository.full_name,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = response.json()
        expected_data = {"error": "GitHub repository not found"}

        self.assertEqual(data, expected_data)

    @responses.activate
    def test_github_repo_unknown_error_throws_error(self):
        mock_offering = create_offering()
        mock_repository = create_repository()

        create_enrollment(
            user_id=self.user.id, offering=mock_offering, kind=db.Role.Kind.INSTRUCTOR
        )

        # Mock a 403 response from GitHub API for repository metadata
        responses.add(
            responses.GET,
            f"{GITHUB_REPOS_API_BASE}/{mock_repository.full_name}",
            status=status.HTTP_403_FORBIDDEN,
        )

        request_data = {
            "title": "Quiz Title",
            "slug": "quiz-slug",
            "visible_at_timestamp": 1740248155,
            "starts_at_timestamp": 1740248155,
            "ends_at_timestamp": 1740248155,
            "github_repository": mock_repository.full_name,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        expected_data = {"error": "There was an error fetching the GitHub repository"}

        self.assertEqual(data, expected_data)

    def test_duplicate_quiz_slug_in_offering_throws_error(self):
        mock_quiz = create_quiz(self.user.id)

        create_enrollment(
            user_id=self.user.id,
            offering=mock_quiz.offering,
            kind=db.Role.Kind.INSTRUCTOR,
        )

        request_data = {
            "title": "Quiz Title",
            "slug": mock_quiz.slug,
            "visible_at_timestamp": 1740248155,
            "starts_at_timestamp": 1740248155,
            "ends_at_timestamp": 1740248155,
            "github_repository": mock_quiz.repository.full_name,
        }

        response = self.client.post(
            self.get_api_endpoint(mock_quiz.offering.course.slug), data=request_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        expected_data = {"error": "Quiz slug already exists"}

        self.assertEqual(data, expected_data)
