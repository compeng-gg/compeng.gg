import courses.models as db
from rest_framework import status
from datetime import datetime, timedelta
from tests.utils import create_offering, create_offering_teams_settings, TestCasesWithUserAuth


class RequestToJoinTeamTests(TestCasesWithUserAuth):
    def test_request_to_join_team_happy_path(self):
        offering = create_offering()
        offering_teams_settings = create_offering_teams_settings(offering)
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )
        
        team = db.Team.objects.create(offering=offering)
        
        request_data = {
            'team_id': team.id,
        }
        
        response = self.client.patch('/api/v0/teams/join/request/', data=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        team_member = db.TeamMember.objects.get(
            enrollment=enrollment,
        )

        self.assertEqual(team_member.membership_type, db.TeamMember.MembershipType.REQUESTED_TO_JOIN)


    def test_request_to_join_team_fails_when_in_another_team(self):
        offering = create_offering()
        offering_teams_settings = create_offering_teams_settings(offering)
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )
        
        team = db.Team.objects.create(offering=offering, name='Team 1')
        existing_team = db.Team.objects.create(offering=offering, name='Team 2')
        
        team_member = db.TeamMember.objects.create(
            enrollment=enrollment,
            team=existing_team,
            membership_type=db.TeamMember.MembershipType.MEMBER,
        )

        request_data = {
            'team_id': team.id,
        }
        
        response = self.client.patch('/api/v0/teams/join/request/', data=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_request_to_join_team_over_capacity(self):
        offering = create_offering()
        offering_teams_settings = create_offering_teams_settings(offering, max_team_size=0)
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )
        
        team = db.Team.objects.create(offering=offering, name='Team 1')

        request_data = {
            'team_id': team.id,
        }
        
        response = self.client.patch('/api/v0/teams/join/request/', data=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_request_to_join_team_past_deadline(self):
        offering = create_offering()
        offering_teams_settings = create_offering_teams_settings(offering, formation_deadline=datetime.now() - timedelta(days=1))
        
        student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)
        
        enrollment = db.Enrollment.objects.create(
            user=self.user,
            role=student_role,
        )
        
        team = db.Team.objects.create(offering=offering, name='Team 1')

        request_data = {
            'team_id': team.id,
        }
        
        response = self.client.patch('/api/v0/teams/join/request/', data=request_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
