from tests.utils import TestCasesWithUserAuth
import courses.models as db
from tests.utils import create_offering, create_student_enrollment, create_offering_teams_settings, create_user
from rest_framework import status
from django.utils.text import slugify


class DeleteTeamTests(TestCasesWithUserAuth):
    def get_api_endpoint(self) -> str:
        return "/api/v0/teams/delete/"

    def test_delete_team_success(self):
        offering = create_offering()
        create_offering_teams_settings(offering)
        enrollment = create_student_enrollment(self.user.id, offering)

        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug=slugify("Team 1"),
        )

        db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )
        
        data = {'team_id': team.id}

        response = self.client.delete(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(db.Team.objects.filter(id=team.id).exists())

    def test_delete_team_fails_if_not_leader(self):
        offering = create_offering()
        create_offering_teams_settings(offering)
        enrollment = create_student_enrollment(self.user.id, offering)

        team = db.Team.objects.create(
            name="Team 1",
            offering=offering,
            github_team_slug=slugify("Team 1"),
        )

        # Create another user as team leader
        leader = create_user("lad")
        leader_enrollment = create_student_enrollment(leader.id, offering)
        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        # Current user is just a member
        db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.MEMBER,
        )

        data = {'team_id': team.id}

        response = self.client.delete(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(db.Team.objects.filter(id=team.id).exists())

    def test_delete_team_fails_if_team_not_found(self):
        data = {'team_id': 123}

        response = self.client.delete(self.get_api_endpoint(), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
