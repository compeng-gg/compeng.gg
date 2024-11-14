import courses.models as db
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.teams.schemas import (
    JoinTeamRequestSerializer,
    LeaveTeamRequestSerializer, 
    ManageTeamMemberRequestSerializer,
    DeleteTeamRequestSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from uuid import UUID
from django.utils import timezone

from dataclasses import dataclass
from courses.teams.utils import IsInstructorOrTA

@dataclass
class TeamEnrollmentData:
    team: db.Team
    team_settings: db.OfferingTeamsSettings
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
    
    try:
        team_settings = db.OfferingTeamsSettings.objects.get(offering=team.offering)
    except db.OfferingTeamsSettings.DoesNotExist:
        raise ValidationError()
    
    return TeamEnrollmentData(
        team=team,
        team_settings=team_settings,
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
        
        team = team_enrollment_data.team
        enrollment = team_enrollment_data.enrollment
        
        
        if db.TeamMember.objects.filter(enrollment=enrollment).count() > 0:
            raise ValidationError()
        
        max_team_size = team_enrollment_data.team_settings.max_team_size
        formation_deadline = team_enrollment_data.team_settings.formation_deadline
        if db.TeamMember.objects.filter(team=team).count() >= max_team_size:
            raise ValidationError()
        
        if formation_deadline < timezone.now():
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
def manage_join_team_request(request):
    from courses.models import TeamMember
    serializer = ManageTeamMemberRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        joiner_name = serializer.validated_data.get('joiner_name')
        approved = serializer.validated_data.get('approved')
        request_id = request.user.id
        
        teamMembers = db.TeamMember.objects.filter(
            team_id=team_id
        )
        
        
        leader = None
        approvedJoiner = None
        for member in teamMembers:
            if member.membership_type == TeamMember.MembershipType.LEADER:
                if member.enrollment.user.id == request_id:
                    leader = member
                else: #If leader is not person requesting operation, throw error
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            elif member.membership_type == TeamMember.MembershipType.REQUESTED_TO_JOIN \
                and member.enrollment.user.username == joiner_name:
                    approvedJoiner = member
        
        if leader == None or approvedJoiner == None:
            raise ValidationError()
        
        if approved:
            approvedJoiner.membership_type = db.TeamMember.MembershipType.MEMBER
            approvedJoiner.save()
        else:
            approvedJoiner.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_team(request):
    serializer = DeleteTeamRequestSerializer(data=request.data)

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
        
        team_empty = False
        
        #Frontend only allows deletion by leader if team is empty
        if team_member.membership_type == db.TeamMember.MembershipType.LEADER:
            team_empty = True
        
        team_member.delete()
        if team_empty:
            team.delete()
    
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teams(request, slug):
    from courses.models import Team, Offering
    try:
        offering = Offering.objects.get(course__slug=slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = []
    for team in Team.objects.filter(offering=offering):
        members = []
        for teamMember in team.members.all():
            members.append({
                'role': teamMember.membership_type,
                'name': teamMember.enrollment.user.username,
            })
        
        data.append({
            'id': team.id,
            'name': team.name,
            'members': members,
        })
    
    return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team(request):
    from courses.teams.schemas import CreateTeamRequestSerializer
    from courses.models import Offering
    serializer = CreateTeamRequestSerializer(data=request.data)

    if serializer.is_valid():
        team_name = serializer.validated_data.get('team_name')
        course_slug = serializer.validated_data.get('course_slug')

        try:
            offering = Offering.objects.get(course__slug=course_slug)
        except Offering.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        try:
            team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.OfferingTeamsSettings.DoesNotExist:
            raise ValidationError()
        
        if team_settings.formation_deadline < timezone.now():
                raise ValidationError()

        try:
            role = db.Role.objects.get(
                kind=db.Role.Kind.STUDENT,
                offering=offering,
            )
        except db.Role.DoesNotExist:
            return Response({'detail': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            enrollment = db.Enrollment.objects.get(
                role=role,
                user=request.user,
            )
        except db.Enrollment.DoesNotExist:
            return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        team = db.Team.objects.create(
            name=team_name,
            offering=offering,
        )

        db.TeamMember.objects.create(
            team=team,
            enrollment=enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        return Response({'id': team.id, 'name': team.name}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_team_settings_for_offering(request, slug):
    from courses.models import Team, Offering
    try:
        offering = Offering.objects.get(course__slug=slug)
        team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
    except (Offering.DoesNotExist, db.OfferingTeamsSettings.DoesNotExist) as e:
        return Response(e, status=status.HTTP_404_NOT_FOUND)
    
    return Response(team_settings)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team_settings_for_offering(request):
    from courses.teams.schemas import CreateTeamSettingsForOfferingRequestSerializer
    serializer = CreateTeamSettingsForOfferingRequestSerializer(data=request.data)

    if serializer.is_valid():
        offering_id = serializer.validated_data.get('offering_id')

        try:
            offering = db.Offering.objects.get(id=offering_id)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

        team = db.OfferingTeamsSettings.objects.create(
            offering=offering,
            max_team_size = serializer.validated_data.get('max_team_size'),
            formation_deadline = serializer.validated_data.get('formation_deadline'),
            show_group_members = serializer.validated_data.get('show_group_members'),
            allow_custom_names = serializer.validated_data.get('allow_custom_names'),
        )

        return Response({'id': team.id, 'name': team.name}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_team_settings_for_offering(request):
    from courses.teams.schemas import UpdateTeamSettingsForOfferingRequestSerializer
    serializer = UpdateTeamSettingsForOfferingRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        offering_id = serializer.validated_data.get('offering_id')
        try:
            offering = db.Offering.objects.get(id=offering_id)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            offering_team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Team setting not found.'}, status=status.HTTP_404_NOT_FOUND)

        max_team_size = serializer.validated_data.get('max_team_size')
        formation_deadline = serializer.validated_data.get('formation_deadline')
        show_group_members = serializer.validated_data.get('show_group_members')
        allow_custom_names = serializer.validated_data.get('allow_custom_names')

        offering_team_settings.max_team_size = max_team_size
        offering_team_settings.formation_deadline = formation_deadline
        offering_team_settings.show_group_members = show_group_members
        offering_team_settings.allow_custom_names = allow_custom_names
        offering_team_settings.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_team_settings_for_offering(request, slug):
    from courses.models import Team, Offering
    try:
        offering = Offering.objects.get(course__slug=slug)
        team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
    except (Offering.DoesNotExist, db.OfferingTeamsSettings.DoesNotExist) as e:
        return Response(e, status=status.HTTP_404_NOT_FOUND)
    
    return Response(team_settings)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team_settings_for_offering(request):
    from courses.teams.schemas import CreateTeamSettingsForOfferingRequestSerializer
    serializer = CreateTeamSettingsForOfferingRequestSerializer(data=request.data)

    if serializer.is_valid():
        offering_id = serializer.validated_data.get('offering_id')

        try:
            offering = db.Offering.objects.get(id=offering_id)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

        team = db.OfferingTeamsSettings.objects.create(
            offering=offering,
            max_team_size = serializer.validated_data.get('max_team_size'),
            formation_deadline = serializer.validated_data.get('formation_deadline'),
            show_group_members = serializer.validated_data.get('show_group_members'),
            allow_custom_names = serializer.validated_data.get('allow_custom_names'),
        )

        return Response({'id': team.id, 'name': team.name}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_team_settings_for_offering(request):
    from courses.teams.schemas import UpdateTeamSettingsForOfferingRequestSerializer
    serializer = UpdateTeamSettingsForOfferingRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        offering_id = serializer.validated_data.get('offering_id')
        try:
            offering = db.Offering.objects.get(id=offering_id)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            offering_team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Team setting not found.'}, status=status.HTTP_404_NOT_FOUND)

        max_team_size = serializer.validated_data.get('max_team_size')
        formation_deadline = serializer.validated_data.get('formation_deadline')
        show_group_members = serializer.validated_data.get('show_group_members')
        allow_custom_names = serializer.validated_data.get('allow_custom_names')

        offering_team_settings.max_team_size = max_team_size
        offering_team_settings.formation_deadline = formation_deadline
        offering_team_settings.show_group_members = show_group_members
        offering_team_settings.allow_custom_names = allow_custom_names
        offering_team_settings.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsInstructorOrTA])
def add_member_to_team(request):
    # Your logic to add a member to a team
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsInstructorOrTA])
def remove_member_from_team(request):
    # Your logic to remove a member from a team
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsInstructorOrTA])
def delete_team(request):
    # Your logic to delete a team
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsInstructorOrTA])
def create_team_with_leader(request):
    # Your logic to create a team and assign a leader
    return Response(status=status.HTTP_201_CREATED)
