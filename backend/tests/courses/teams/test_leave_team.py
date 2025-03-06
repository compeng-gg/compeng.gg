from tests.utils import TestCasesWithUserAuth, create_offering, create_student_enrollment
import courses.models as db
from rest_framework import status
from unittest.mock import patch

# Dummy container to simulate the object returned by get_student_enrollment_for_team.
class DummyTeamEnrollment:
    def __init__(self, enrollment, team):
        self.enrollment = enrollment
        self.team = team

class LeaveTeamTests(TestCasesWithUserAuth):
    def get_api_endpoint(self) -> str:
        return "/api/v0/teams/leave/"

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_leave_team_as_member_success(self, mock_get_enrollment):
        # Setup: create an offering and a team.
        offering = create_offering()
        team = db.Team.objects.create(
            name="Test Team",
            offering=offering,
            github_team_slug="test-team"
        )
        # Create an enrollment for the authenticated user.
        enrollment = create_student_enrollment(self.user.id, offering)
        # Create a team member with membership type MEMBER (non-leader).
        team_member = db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.MEMBER,
        )
        # Patch the helper to return our dummy object.
        mock_get_enrollment.return_value = DummyTeamEnrollment(enrollment, team)

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # The team member record should be deleted...
        self.assertFalse(db.TeamMember.objects.filter(id=team_member.id).exists())
        # ...but the team should still exist.
        self.assertTrue(db.Team.objects.filter(id=team.id).exists())

    @patch("courses.teams.api.get_student_enrollment_for_team")
    def test_leave_team_as_leader_success(self, mock_get_enrollment):
        # Setup: create an offering and a team.
        offering = create_offering()
        team = db.Team.objects.create(
            name="Test Team",
            offering=offering,
            github_team_slug="test-team"
        )
        # Create an enrollment for the authenticated user.
        enrollment = create_student_enrollment(self.user.id, offering)
        # Create a team member with membership type LEADER.
        team_member = db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )
        # Return our dummy enrollment and team.
        mock_get_enrollment.return_value = DummyTeamEnrollment(enrollment, team)

        data = {
            "team_id": team.id,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # The team member record should be deleted...
        self.assertFalse(db.TeamMember.objects.filter(id=team_member.id).exists())
        # ...and since the leader was leaving, the entire team should also be deleted.
        self.assertFalse(db.Team.objects.filter(id=team.id).exists())

    def test_leave_team_invalid_data(self):
        # Test sending an empty payload so that serializer errors are triggered.
        response = self.client.patch(self.get_api_endpoint(), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.json()
        # The serializer is expected to complain about missing "team_id".
        self.assertIn("team_id", errors)
