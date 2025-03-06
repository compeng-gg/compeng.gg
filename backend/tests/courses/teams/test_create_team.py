from tests.utils import TestCasesWithUserAuth
import courses.models as db
from django.utils import timezone
from tests.utils import create_offering, create_student_enrollment, create_offering_teams_settings, create_student_role
from rest_framework import status
from unittest.mock import patch

class CreateTeamTests(TestCasesWithUserAuth):
    def get_api_endpoint(self) -> str:
        return "/api/v0/teams/create/"

    @patch("courses.teams.api.create_student_team_and_fork", return_value=True)
    def test_create_team_success(self, mock_create_team):
        offering = create_offering()
        create_offering_teams_settings(offering)
        create_student_enrollment(self.user.id, offering)

        data = {
            "team_name": "Team 1",
            "course_slug": offering.course.slug,
            "offering_slug": offering.slug,
        }
        print(data)

        response = self.client.post(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(db.Team.objects.count(), 1)
        self.assertEqual(db.Team.objects.first().name, "Team 1")

    @patch("courses.teams.api.create_student_team_and_fork", return_value=False)
    def test_create_team_github_failure(self, mock_create_team):
        offering = create_offering()
        create_offering_teams_settings(offering)
        create_student_enrollment(self.user.id, offering)

        data = {
            "team_name": "Test Team",
            "course_slug": offering.course.slug,
            "offering_slug": offering.slug,
        }

        response = self.client.post(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Failed to create github team and fork"})

    @patch("courses.teams.api.create_student_team_and_fork", return_value=True)
    def test_create_team_fails_without_enrollment(self, mock_create_team):
        offering = create_offering()
        create_offering_teams_settings(offering)
        create_student_role(offering)

        data = {
            "team_name": "Team 1",
            "course_slug": offering.course.slug,
            "offering_slug": offering.slug,
        }

        response = self.client.post(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), {"detail": "Enrollment not found."})

    @patch("courses.teams.api.create_student_team_and_fork", return_value=True)
    def test_create_team_after_deadline_fails(self, mock_create_team):
        offering = create_offering()
        create_offering_teams_settings(offering=offering, formation_deadline=timezone.now() - timezone.timedelta(days=1))
        create_student_enrollment(self.user.id, offering)

        data = {
            "team_name": "Late Team", 
            "course_slug": offering.course.slug,
            "offering_slug": offering.slug,
        }
        print(data)

        response = self.client.post(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {"detail": "Team formation deadline has passed."})

    @patch("courses.teams.api.create_student_team_and_fork", return_value=True)
    def test_create_team_with_missing_data_fails(self, mock_create_team):
        response = self.client.post(self.get_api_endpoint(), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_name", response.json())
        self.assertIn("course_slug", response.json())
