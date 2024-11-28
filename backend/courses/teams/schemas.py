from rest_framework import serializers
import courses.models as db

class JoinTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)

class ManageTeamMemberRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)
    joiner_name = serializers.CharField(max_length=255, required=True)
    approved = serializers.BooleanField(required=True)
        
class LeaveTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)

class DeleteTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)

class CreateTeamRequestSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=255, required=True)
    course_slug = serializers.CharField(max_length=255, required=True)

class CreateTeamSettingsForOfferingRequestSerializer(serializers.Serializer):
    offering_id = serializers.UUIDField(required=True)
    max_team_size = serializers.IntegerField(required=True)
    formation_deadline = serializers.DateTimeField(required=True)
    show_group_members = serializers.BooleanField(default=True)
    allow_custom_names = serializers.BooleanField(default=False)

class UpdateTeamSettingsForOfferingRequestSerializer(serializers.Serializer):
    offering_id = serializers.UUIDField(required=True)
    max_team_size = serializers.IntegerField(required=True)
    formation_deadline = serializers.DateTimeField(required=True)
    show_group_members = serializers.BooleanField(default=True)
    allow_custom_names = serializers.BooleanField(default=False)
    
class createTeamWithLeaderRequestSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=255, required=True)
    course_slug = serializers.CharField(max_length=255, required=True)
    leader_name = serializers.CharField(max_length=255, required=True)
    
class removeTeamMemberRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)
    member_id = serializers.UUIDField(required=True)
    
class addTeamMemberRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)
    member_id = serializers.UUIDField(required=True)