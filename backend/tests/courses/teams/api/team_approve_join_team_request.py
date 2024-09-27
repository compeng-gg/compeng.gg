import courses.models as db
from rest_framework import status
from tests.utils import create_offering, TestCasesWithUserAuth
from django.contrib.auth.models import User


class ApproveJoinTeamRequestTests(TestCasesWithUserAuth):
    def test_approve_join_team_request_happy_path(self):
        offering = create_offering()
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        requesting_user = User.objects.create()

        enrollment = db.Enrollment.objects.create(
            user=requesting_user,
            role=student_role,
        )

        team = db.Team.objects.create(offering=offering)

        team_member = db.TeamMember.objects.create(
            enrollment=enrollment,
            team=team,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        request_data = {
            'team_id': team.id,
            'user_id': requesting_user.id
        }

        response = self.client.patch('/api/v0/courses/team/join/approve/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        team_member.refresh_from_db()

        self.assertEqual(team_member.membership_type, db.TeamMember.MembershipType.MEMBER)

    def test_approve_join_team_request_fails_when_request_dne(self):
        offering = create_offering()
        
        requesting_user = User.objects.create()

        team = db.Team.objects.create(offering=offering)

        request_data = {
            'team_id': team.id,
            'user_id': requesting_user.id
        }

        response = self.client.patch('/api/v0/courses/team/join/approve/', data=request_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
