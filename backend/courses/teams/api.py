import courses.models as db
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from courses.teams.schemas import (
    JoinTeamRequestSerializer,
    LeaveTeamRequestSerializer, 
    ManageTeamMemberRequestSerializer,
    DeleteTeamRequestSerializer,
    CreateTeamRequestSerializer,
    createTeamWithLeaderRequestSerializer,
    CreateTeamSettingsForOfferingRequestSerializer,
    UpdateTeamSettingsForOfferingRequestSerializer,
    removeTeamMemberRequestSerializer,
    addTeamMemberRequestSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from uuid import UUID
from django.utils import timezone
from github_app.utils import create_student_team_and_fork, add_student_to_github_team
from slugify import slugify
from courses.models import Offering, TeamMember, Team

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
        return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    course_slug = team.offering.course.slug
    try:
        offering = db.Offering.objects.get(
            course__slug=course_slug,
            active=True
        )
    except db.Offering.DoesNotExist:
        return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

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
            user_id=user_id,
        )
    except db.Enrollment.DoesNotExist:
        return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        team_settings = db.OfferingTeamsSettings.objects.get(offering=team.offering)
    except db.OfferingTeamsSettings.DoesNotExist:
        return Response({'detail': 'Team settings not found.'}, status=status.HTTP_404_NOT_FOUND)
    
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
        
        # Validate user does not break membership conditions
        if db.TeamMember.objects.filter(enrollment=enrollment).count() > 0:
            return Response({'detail': 'User is already in a team.'}, status=status.HTTP_400_BAD_REQUEST)
        
        max_team_size = team_enrollment_data.team_settings.max_team_size
        formation_deadline = team_enrollment_data.team_settings.formation_deadline
        if db.TeamMember.objects.filter(team=team).count() >= max_team_size:
            return Response({'detail': 'Team is full.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if formation_deadline < timezone.now():
            return Response({'detail': 'Team formation deadline has passed.'}, status=status.HTTP_400_BAD_REQUEST)
            
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
    serializer = ManageTeamMemberRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        joiner_name = serializer.validated_data.get('joiner_name')
        approved = serializer.validated_data.get('approved')
        request_id = request.user.id
        try:
            team = db.Team.objects.get(id=team_id)
        except db.Team.DoesNotExist:
            raise ValidationError()
    
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
        
        if leader == None:
            return Response({'detail': 'Leader not found.'}, status=status.HTTP_404_NOT_FOUND)
        if approvedJoiner == None:
            return Response({'detail': 'Joiner not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if approved:
            add_student_to_github_team(request.user, team.github_team_slug)
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
        # Check for leader credentials
        team_id = serializer.validated_data.get('team_id')
        user_id = request.user.id

        team_enrollment_data = get_student_enrollment_for_team(
            team_id=team_id,
            user_id=user_id,
        )
        print(team_enrollment_data)

        if isinstance(team_enrollment_data, Response):
            return team_enrollment_data

        enrollment = team_enrollment_data.enrollment
        team = team_enrollment_data.team
        try:
            team_member = db.TeamMember.objects.get(
                team_id=team_id,
                enrollment=enrollment,
            )
        except db.TeamMember.DoesNotExist:
            return Response({'detail': 'Team member not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if team_member.membership_type != db.TeamMember.MembershipType.LEADER:
            return Response({'detail': 'Only team leader can delete team.'}, status=status.HTTP_401_UNAUTHORIZED)
  
        teamMembers = db.TeamMember.objects.filter(team=team)
        teamMembers.delete()
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
            return Response({'detail': 'Team member not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        team_empty = False
        
        # Frontend only allows deletion by leader if team is empty
        if team_member.membership_type == db.TeamMember.MembershipType.LEADER:
            team_empty = True
        
        team_member.delete()
        if team_empty:
            team.delete()
    
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def teams(request, course_slug, offering_slug):
    try:
        offering = Offering.objects.get(course__slug=course_slug, slug=offering_slug)
    except Offering.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = []
    for team in Team.objects.filter(offering=offering):
        members = []
        for teamMember in team.members.all():
            members.append({
                'id': teamMember.enrollment.user.id,
                'role': teamMember.membership_type,
                'name': teamMember.enrollment.user.username,
            })
        
        data.append({
            'id': team.id,
            'name': team.name,
            'members': members,
        })
        
    print("team data:", data)
    
    return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team(request):
    serializer = CreateTeamRequestSerializer(data=request.data)

    if serializer.is_valid():
        # Validations
        team_name = serializer.validated_data.get('team_name')
        course_slug = serializer.validated_data.get('course_slug')
        offering_slug = serializer.validated_data.get('offering_slug')
        try:
            offering = Offering.objects.get(course__slug=course_slug, slug=offering_slug)
        except Offering.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.OfferingTeamsSettings.DoesNotExist:
            return Response({'detail': 'Team settings not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if team_settings.formation_deadline < timezone.now():
            return Response({'detail': 'Team formation deadline has passed.'}, status=status.HTTP_400_BAD_REQUEST)

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

        # Create team models
        success = create_student_team_and_fork(offering, team_name, request.user)
        if not success:
            print('Failed to create github team and fork')
            return Response({'detail': 'Failed to create github team and fork'}, status=status.HTTP_400_BAD_REQUEST)
        
        team = db.Team.objects.create(
            name=team_name,
            offering=offering,
            created_at=timezone.now(),
            github_team_slug=slugify(team_name)
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
def get_team_settings_for_offering(request, course_slug, offering_slug):
    try:
        offering = Offering.objects.get(course__slug=course_slug, slug=offering_slug)
        team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        data = {
            "max_team_size": team_settings.max_team_size,
            "formation_deadline": team_settings.formation_deadline,
        }
    except (Offering.DoesNotExist) as e:
        return Response(e, status=status.HTTP_404_NOT_FOUND)
    except db.Offering.MultipleObjectsReturned:
        return Response({'detail': 'Multiple offerings found with the same slugs. This should not happen.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except db.OfferingTeamsSettings.DoesNotExist:
        print("Teams Setttings for offering not instantiated")
        data = {
            "max_team_size": None,
            "formation_deadline": None,
        }
    
    return Response(data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team_settings_for_offering(request, course_slug, offering_slug):
    try:
        offering = Offering.objects.get(course__slug=course_slug, slug=offering_slug)
    except db.Offering.DoesNotExist:
        return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)
    except db.Offering.MultipleObjectsReturned:
        return Response({'detail': 'Multiple offerings found with the same slugs. This should not happen.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Fail if teams settings already exists
    try: 
        _ = db.OfferingTeamsSettings.objects.get(offering=offering)
        return Response({'detail': 'Team Settings already exists'}, status=status.HTTP_404_NOT_FOUND)
    except db.OfferingTeamsSettings.DoesNotExist:
        pass

    teamSettings = db.OfferingTeamsSettings.objects.create(offering=offering)
    data = {
        "max_team_size": teamSettings.max_team_size,
        "formation_deadline": teamSettings.formation_deadline
    }
    return Response(data, status=status.HTTP_201_CREATED)

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_team_settings_for_offering(request, course_slug, offering_slug):
    serializer = UpdateTeamSettingsForOfferingRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            offering = Offering.objects.get(course__slug=course_slug, slug=offering_slug)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)
        except db.Offering.MultipleObjectsReturned:
            return Response({'detail': 'Multiple offerings found with the same slugs. This should not happen.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            offering_team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Team setting not found.'}, status=status.HTTP_404_NOT_FOUND)

        max_team_size = serializer.validated_data.get('max_team_size')
        formation_deadline = serializer.validated_data.get('formation_deadline')

        offering_team_settings.max_team_size = max_team_size
        offering_team_settings.formation_deadline = formation_deadline
        offering_team_settings.save()

        data = {
            "max_team_size": offering_team_settings.max_team_size,
            "formation_deadline": offering_team_settings.formation_deadline
        }
        return Response(data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# @permission_classes([IsInstructorOrTA])
# def add_member_to_team(request):
#     print("Adding member to team")
#     serializer = addTeamMemberRequestSerializer(data=request.data)
    
#     if serializer.is_valid():
#         team_id = serializer.validated_data.get('team_id')
#         member_id = serializer.validated_data.get('member_id')
        
#         try:
#             # Retrieve the target team
#             team = db.Team.objects.get(id=team_id)
#         except db.Team.DoesNotExist:
#             return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
        
#         try:
#             # Retrieve the member
#             member = db.TeamMember.objects.get(id=member_id)
#         except db.TeamMember.DoesNotExist:
#             return Response({'detail': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)
        
#         # Check if the member is already in a team
#         if member.team is not None:
#             return Response(
#                 {'detail': f'Member is already in team {member.team.name}.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         # Add the member to the target team
#         member.team = team
#         member.save()
        
#         return Response({'detail': 'Member added to the team successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
#     # Return validation errors
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsInstructorOrTA])
def add_member_to_team(request):
    print("Add member to team")
    
    serializer = addTeamMemberRequestSerializer(data=request.data)
    print("Serializer data:", request.data)
    
    if serializer.is_valid():
        print("Serializer is valid")
        team_id = serializer.validated_data.get('team_id')
        member_id = serializer.validated_data.get('member_id')  # Assuming this is the enrollment ID
        print("Team ID:", team_id, "Member ID (enrollment):", member_id)

        try:
            # Retrieve the team
            team = db.Team.objects.get(id=team_id)
            print("Team found:", team)
        except db.Team.DoesNotExist:
            print("Team not found")
            return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve the Enrollment to get the user
            enrollment = db.Enrollment.objects.select_related('user').get(id=member_id)
            print("Enrollment found:", enrollment)
        except db.Enrollment.DoesNotExist:
            print("Enrollment not found")
            return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the enrollment is already linked to a team
        existing_membership = db.TeamMember.objects.filter(enrollment=enrollment).first()
        if existing_membership:
            print("Enrollment already in a team:", existing_membership.team.name)
            return Response(
                {'detail': f'This user is already in team {existing_membership.team.name}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new TeamMember and link the enrollment to the team
        new_member = db.TeamMember.objects.create(enrollment=enrollment, team=team, membership_type=db.TeamMember.MembershipType.MEMBER)
        new_member.save()
        print("User added successfully as a team member")
        return Response({'detail': 'User added to the team successfully.'}, status=status.HTTP_204_NO_CONTENT)

    print("Serializer invalid:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsInstructorOrTA])
def remove_member_from_team(request):
    print("Remove member from team initiated")

    # Log the incoming request data for debugging
    print("Request data:", request.data)

    serializer = removeTeamMemberRequestSerializer(data=request.data)

    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        member_id = serializer.validated_data.get('member_id')  # Assuming this is the enrollment ID

        print(f"Valid serializer data: team_id={team_id}, member_id={member_id}")

        try:
            # Retrieve the team
            team = db.Team.objects.get(id=team_id)
            print(f"Team found: {team}")
        except db.Team.DoesNotExist:
            print("Team not found")
            return Response({'detail': 'Team not found. Please check the team_id.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve the Enrollment to get the member
            enrollment = db.Enrollment.objects.get(id=member_id)
            print(f"Enrollment found: {enrollment}")
        except db.Enrollment.DoesNotExist:
            print("Enrollment not found")
            return Response({'detail': 'Enrollment not found. Please check the member_id.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Check if the enrollment is linked to a TeamMember in the specified team
            member = db.TeamMember.objects.get(enrollment=enrollment, team=team)
            print(f"Team member found: {member}")
        except db.TeamMember.DoesNotExist:
            print("Member not found in the specified team")
            return Response(
                {'detail': f'This member does not belong to the specified team {team.name}.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Perform the deletion
        member.delete()
        print(f"Member {member} successfully removed from team {team}")
        return Response({'detail': 'Member removed from the team successfully.'}, status=status.HTTP_204_NO_CONTENT)

    # Log serializer errors for debugging
    print("Invalid serializer data:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsInstructorOrTA])
def delete_team_as_admin(request):
    serializer = DeleteTeamRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        team_id = serializer.validated_data.get('team_id')
        
        try:
            team = db.Team.objects.get(id=team_id)
        except db.Team.DoesNotExist:
            return Response({'detail': 'Team not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        team.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsInstructorOrTA])
def create_team_with_leader(request):
    print("Incoming request data:", request.data)  # Log request data

    serializer = createTeamWithLeaderRequestSerializer(data=request.data)

    if serializer.is_valid():
        team_name = serializer.validated_data.get('team_name')
        course_slug = serializer.validated_data.get('course_slug')
        leader_id = serializer.validated_data.get('leader_id')

        try:
            offering = db.Offering.objects.get(course__slug=course_slug)
        except db.Offering.DoesNotExist:
            return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            team_settings = db.OfferingTeamsSettings.objects.get(offering=offering)
        except db.OfferingTeamsSettings.DoesNotExist:
            return Response({'detail': 'Team settings not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            role = db.Role.objects.get(
                kind=db.Role.Kind.STUDENT,
                offering=offering,
            )
        except db.Role.DoesNotExist:
            return Response({'detail': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            leader_enrollment = db.Enrollment.objects.get(
                role=role,
                user_id=leader_id,
            )
        except db.Enrollment.DoesNotExist:
            return Response({'detail': 'Leader not found.'}, status=status.HTTP_404_NOT_FOUND)

        team = db.Team.objects.create(
            name=team_name,
            offering=offering,
        )

        db.TeamMember.objects.create(
            team=team,
            enrollment=leader_enrollment,
            membership_type=db.TeamMember.MembershipType.LEADER,
        )

        return Response({'id': team.id, 'name': team.name}, status=status.HTTP_201_CREATED)

    print("Serializer validation errors:", serializer.errors)  # Log serializer errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_team_status(request, slug):
    try:
        offering = db.Offering.objects.get(course__slug=slug)
    except db.Offering.DoesNotExist:
        return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

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

    team_member = TeamMember.objects.filter(enrollment=enrollment).first()
    if team_member:
        team_data = {
            'team_id': team_member.team.id,
            'team_name': team_member.team.name,
            'membership_type': team_member.membership_type,
        }
    else:
        team_data = None

    return Response({'user_id': request.user.id, 'team': team_data})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_role(request, slug):
    try:
        # Find the offering using the provided slug
        offering = db.Offering.objects.get(course__slug=slug, active=True)
    except db.Offering.DoesNotExist:
        return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Fetch the role for the user in the offering
        enrollment = db.Enrollment.objects.get(
            user=request.user,
            role__offering=offering,
        )
        role = enrollment.role
    except db.Enrollment.DoesNotExist:
        return Response({'detail': 'Enrollment not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Return the role information
    return Response({
        'user_id': request.user.id,
        'offering': offering.name,
        'role': role.kind,  # This will return the role enum value (e.g., 'STUDENT')
    })
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_enrolled_students(request, slug):
    """
    Retrieve a list of enrolled students for a given offering.
    """
    try:
        # Retrieve the offering based on the slug
        offering = db.Offering.objects.get(course__slug=slug, active=True)
    except db.Offering.DoesNotExist:
        return Response({'detail': 'Offering not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Filter enrollments for students in the offering
    student_enrollments = db.Enrollment.objects.filter(
        role__kind=db.Role.Kind.STUDENT,  # Filter by student role
        role__offering=offering
    ).select_related('user')  # Optimize query by prefetching user details
    
    print(student_enrollments)

    # Serialize the data, use 'username', 'first_name', and 'last_name' if 'name' doesn't exist
    students = [
    {
        'id': enrollment.user.id,
        'name': getattr(
            enrollment.user,
            'name',
            getattr(
                enrollment.user,
                'username',  # Use username as a fallback if name, first_name, and last_name are missing
                f"{getattr(enrollment.user, 'first_name', '')} {getattr(enrollment.user, 'last_name', '')}".strip()
            )
        ),
        'email': getattr(enrollment.user, 'email', ''),  # Assuming 'email' exists in the user model
    }
    for enrollment in student_enrollments
]
    
    print("Done:", students)

    return Response(students, status=status.HTTP_200_OK)
