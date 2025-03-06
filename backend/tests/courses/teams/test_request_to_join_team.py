from tests.utils import TestCasesWithUserAuth, create_offering, create_student_enrollment
import courses.models as db
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model

User = get_user_model()

# Dummy classes to simulate get_student_enrollment_for_team's return value.
class DummyTeamSettings:
    def __init__(self, max_team_size, formation_deadline):
        self.max_team_size = max_team_size
        self.formation_deadline = formation_deadline

class DummyTeamEnrollmentData:
    def __init__(self, enrollment, team, team_settings):
        self.enrollment = enrollment
        self.team = team
        self.team_settings = team_settings

class RequestToJoinTeamTests(TestCasesWithUserAuth):

    def get_api_endpoint(self) -> str:
        return "/api/v0/teams/join/request/"

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_request_to_join_team_success(self, mock_get_enrollment):
        """
        A successful join request:
          - The user is not in a team already.
          - The team is not full.
          - The formation deadline is in the future.
        """
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        enrollment = create_student_enrollment(self.user.id, offering)
        # Set team settings with room for 3 members and a deadline in the future.
        team_settings = DummyTeamSettings(
            max_team_size=3, 
            formation_deadline=timezone.now() + timedelta(days=1)
        )
        dummy_data = DummyTeamEnrollmentData(enrollment, team, team_settings)
        mock_get_enrollment.return_value = dummy_data

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify a new TeamMember record was created with membership_type REQUESTED_TO_JOIN.
        team_member = db.TeamMember.objects.filter(team=team, enrollment=enrollment).first()
        self.assertIsNotNone(team_member)
        self.assertEqual(team_member.membership_type, db.TeamMember.MembershipType.REQUESTED_TO_JOIN)

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_request_already_in_team(self, mock_get_enrollment):
        """
        A failure when the user is already in a team.
        """
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        enrollment = create_student_enrollment(self.user.id, offering)
        team_settings = DummyTeamSettings(
            max_team_size=3, 
            formation_deadline=timezone.now() + timedelta(days=1)
        )
        dummy_data = DummyTeamEnrollmentData(enrollment, team, team_settings)
        mock_get_enrollment.return_value = dummy_data

        # Create an existing TeamMember for this enrollment.
        db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.MEMBER
        )

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "User is already in a team."})

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_request_team_full(self, mock_get_enrollment):
        """
        A failure when the team is full.
        """
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        enrollment = create_student_enrollment(self.user.id, offering)
        # Set max_team_size to 1, so if there is any existing member, the team is full.
        team_settings = DummyTeamSettings(
            max_team_size=1, 
            formation_deadline=timezone.now() + timedelta(days=1)
        )
        dummy_data = DummyTeamEnrollmentData(enrollment, team, team_settings)
        mock_get_enrollment.return_value = dummy_data

        # Create a team member for a different enrollment to fill the team.
        other_user = User.objects.create_user(username="other", password="pass")
        other_enrollment = create_student_enrollment(other_user.id, offering)
        db.TeamMember.objects.create(
            team=team,
            enrollment=other_enrollment,
            membership_type=db.TeamMember.MembershipType.MEMBER
        )

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Team is full."})

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_request_after_deadline(self, mock_get_enrollment):
        """
        A failure when the team formation deadline has passed.
        """
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        enrollment = create_student_enrollment(self.user.id, offering)
        # Set a formation deadline in the past.
        team_settings = DummyTeamSettings(
            max_team_size=3, 
            formation_deadline=timezone.now() - timedelta(days=1)
        )
        dummy_data = DummyTeamEnrollmentData(enrollment, team, team_settings)
        mock_get_enrollment.return_value = dummy_data

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Team formation deadline has passed."})

