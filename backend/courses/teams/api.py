import courses.models as db
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.teams.schemas import JoinTeamRequestSerializer, LeaveTeamRequestSerializer, ApproveTeamMemberRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from uuid import UUID

from dataclasses import dataclass

@dataclass
class TeamEnrollmentData:
    team: db.Team
    enrollment: db.Enrollment


def get_student_enrollment_for_team(team_id: UUID, user_id: int) -> TeamEnrollmentData:
    try:
        team = db.Team.objects.get(
            id=team_id,
        )
    except db.Team.DoesNotExist:
        raise ValidationError()
    
    course_slug = team.offering.course.slug
    
    try:
        offering = db.Offering.objects.get(
            course__slug=course_slug,
            active=True
        )
    except db.Offering.DoesNotExist:
        raise ValidationError()

    try:
        role = db.Role.objects.get(
            kind=db.Role.Kind.STUDENT,
            offering=offering,
        )
    except db.Role.DoesNotExist:
        raise ValidationError()
    
    try:
        enrollment = db.Enrollment.objects.get(
            role=role,
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        raise ValidationError()
    
    return TeamEnrollmentData(
        team=team,
        enrollment=enrollment,
    )


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def request_to_join_team(request):
    serializer = JoinTeamRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        user_id = request.user.id

        team_enrollment_data = get_student_enrollment_for_team(
            team_id=team_id,
            user_id=user_id,
        )
        enrollment = team_enrollment_data.enrollment
        
        if db.TeamMember.objects.filter(enrollment=enrollment).count() > 0:
            raise ValidationError()

        db.TeamMember.objects.create(
            team_id=team_id,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def approve_join_team_request(request):
    serializer = ApproveTeamMemberRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        user_id = serializer.validated_data.get('user_id')

        team_enrollment_data = get_student_enrollment_for_team(
            team_id=team_id,
            user_id=user_id,
        )
        enrollment = team_enrollment_data.enrollment

        try:
            team_member = db.TeamMember.objects.get(
                team_id=team_id,
                enrollment=enrollment,
                membership_type=db.TeamMember.MembershipType.REQUESTED_TO_JOIN,
            )   
        except db.TeamMember.DoesNotExist:
            raise ValidationError()

        team_member.membership_type = db.TeamMember.MembershipType.MEMBER
        team_member.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_team(request):
    serializer = LeaveTeamRequestSerializer(data=request.data)

    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        user_id = request.user.id

        team_enrollment_data = get_student_enrollment_for_team(
            team_id=team_id,
            user_id=user_id,
        )
        enrollment = team_enrollment_data.enrollment
        team = team_enrollment_data.team

        try:
            team_member = db.TeamMember.objects.get(
                team_id=team_id,
                enrollment=enrollment,
            )
        except db.TeamMember.DoesNotExist:
            raise ValidationError()
        
        if team_member.membership_type != db.TeamMember.MembershipType.LEADER:
            raise ValidationError()
  
        team.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def leave_team(request):
    serializer = LeaveTeamRequestSerializer(data=request.data)

    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        user_id = request.user.id

        team_enrollment_data = get_student_enrollment_for_team(
            team_id=team_id,
            user_id=user_id,
        )
        enrollment = team_enrollment_data.enrollment
        team = team_enrollment_data.team
        
        try:
            team_member = db.TeamMember.objects.get(
                team=team,
                enrollment=enrollment,
            )
        except db.TeamMember.DoesNotExist:
            raise ValidationError()
        
        if team_member.membership_type == db.TeamMember.MembershipType.LEADER:
            raise ValidationError()
        
        team_member.delete()
    
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)