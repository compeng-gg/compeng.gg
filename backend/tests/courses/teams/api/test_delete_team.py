import courses.models as db
from rest_framework import status
from tests.utils import create_offering, TestCasesWithUserAuth
import pytest

class DeleteTeamTests(TestCasesWithUserAuth):
    def test_delete_team_happy_path(self):
        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )

        team = db.Team.objects.create(offering=offering)

        db.TeamMember.objects.create(
            enrollment=enrollment,
            team=team,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        request_data = {
            'team_id': team.id,
        }

        response = self.client.delete('/api/v0/courses/team/delete/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with pytest.raises(db.Team.DoesNotExist):
            team.refresh_from_db()


    def test_delete_team_fails_when_not_team_leader(self):
        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )

        team = db.Team.objects.create(offering=offering)

        db.TeamMember.objects.create(
            enrollment=enrollment,
            team=team,
            membership_type=db.TeamMember.MembershipType.MEMBER,
        )

        request_data = {
            'team_id': team.id,
        }

        response = self.client.delete('/api/v0/courses/team/delete/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        team.refresh_from_db()

    
    def test_delete_team_fails_when_not_in_team(self):
        offering = create_offering()

        team = db.Team.objects.create(offering=offering)

        request_data = {
            'team_id': team.id,
        }

        response = self.client.delete('/api/v0/courses/team/delete/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        team.refresh_from_db()
