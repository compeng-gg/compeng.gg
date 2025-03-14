from tests.utils import TestCasesWithUserAuth, create_offering, create_student_enrollment, create_user, create_student_role
import courses.models as db
from rest_framework import status
from unittest.mock import patch


class ApproveJoinTeamRequestTests(TestCasesWithUserAuth):
    def get_api_endpoint(self) -> str:
        return "/api/v0/teams/join/manage/"
    
    @patch("courses.teams.api.add_student_to_github_team")
    def test_approve_join_request_success(self, mock_add_student):
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        leader_enrollment = create_student_enrollment(self.user.id, offering)
        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )
        joiner_user = create_user('joiner')
        joiner_enrollment = db.Enrollment.objects.create(
            role=leader_enrollment.role,  # assuming role is compatible
            user=joiner_user
        )
        joiner_member = db.TeamMember.objects.create(
            team=team,
            enrollment=joiner_enrollment,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        data = {
            "team_id": team.id,
            "joiner_name": "joiner",
            "approved": True,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        joiner_member.refresh_from_db()
        self.assertEqual(joiner_member.membership_type, db.TeamMember.MembershipType.MEMBER)

    @patch("courses.teams.api.add_student_to_github_team")
    def test_reject_join_request_success(self, mock_add_student):
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        leader_enrollment = create_student_enrollment(self.user.id, offering)
        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )
        joiner_user = create_user('joiner')
        joiner_enrollment = db.Enrollment.objects.create(
            role=leader_enrollment.role,
            user=joiner_user
        )
        joiner_member = db.TeamMember.objects.create(
            team=team,
            enrollment=joiner_enrollment,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        data = {
            "team_id": team.id,
            "joiner_name": "joiner",
            "approved": False,
        }

        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db.TeamMember.objects.filter(id=joiner_member.id).exists())

    def test_non_leader_request_returns_unauthorized(self):
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        other_user = create_user('leader')
        leader_enrollment = db.Enrollment.objects.create(
            role=create_student_role(offering),
            user=other_user
        )
        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )
        joiner_user = create_user('joiner')
        joiner_enrollment = db.Enrollment.objects.create(
            role=leader_enrollment.role,
            user=joiner_user
        )
        db.TeamMember.objects.create(
            team=team,
            enrollment=joiner_enrollment,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        data = {
            "team_id": team.id,
            "joiner_name": "joiner",
            "approved": True,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        # Since the requester is not the leader, we expect a 401 Unauthorized.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_joiner_not_found(self):
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        leader_enrollment = create_student_enrollment(self.user.id, offering)
        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        data = {
            "team_id": team.id,
            "joiner_name": "nonexistent",
            "approved": True,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Joiner not found."})

    def test_leader_not_found_returns_404(self):
        offering = create_offering()
        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug="team-1"
        )
        joiner_user = create_user('joiner')
        joiner_enrollment = db.Enrollment.objects.create(
            role=create_student_role(offering),
            user=joiner_user
        )
        db.TeamMember.objects.create(
            team=team,
            enrollment=joiner_enrollment,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        data = {
            "team_id": team.id,
            "joiner_name": "joiner",
            "approved": True,
        }
        response = self.client.patch(self.get_api_endpoint(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Leader not found."})
