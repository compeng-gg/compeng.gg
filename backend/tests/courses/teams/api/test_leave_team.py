import courses.models as db
from rest_framework import status
from tests.utils import create_offering, TestCasesWithUserAuth
import pytest


class LeaveTeamTests(TestCasesWithUserAuth):
    def test_leave_team_happy_path(self):
        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )

        team = db.Team.objects.create(offering=offering)

        team_member = db.TeamMember.objects.create(
            enrollment=enrollment,
            team=team,
            membership_type=db.TeamMember.MembershipType.MEMBER,
        )

        request_data = {
            'team_id': team.id,
        }

        response = self.client.patch('/api/v0/courses/team/leave/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        with pytest.raises(db.TeamMember.DoesNotExist):
            team_member.refresh_from_db()


    def test_leave_team_fails_when_requestor_is_team_leader(self):
        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )

        team = db.Team.objects.create(offering=offering)

        team_member = db.TeamMember.objects.create(
            enrollment=enrollment,
            team=team,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        request_data = {
            'team_id': team.id,
        }

        response = self.client.patch('/api/v0/courses/team/leave/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        team_member.refresh_from_db()
