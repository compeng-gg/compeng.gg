from rest_framework import serializers
import courses.models as db
from django.utils import timezone

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
    max_team_size = serializers.IntegerField(required=True)
    formation_deadline = serializers.DateTimeField(required=True)

    def validate_max_team_size(self, value):
        if value < 0:
            raise serializers.ValidationError("Max team size must be greater than 1")
        if value > 2147483647:  # Max value for a 32-bit integer
            raise serializers.ValidationError("Max team size exceeds the allowed limit.")
        return value

    def validate_formation_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Formation deadline cannot be in the past.")
        return value

class UpdateTeamSettingsForOfferingRequestSerializer(serializers.Serializer):
    max_team_size = serializers.IntegerField(required=True)
    formation_deadline = serializers.DateTimeField(required=True)

    def validate_max_team_size(self, value):
        if value < 1:
            raise serializers.ValidationError("Max team size must be greater than 1")
        if value > 2147483647:  # Max value for a 32-bit integer
            raise serializers.ValidationError("Max team size exceeds the allowed limit.")
        return value

    def validate_formation_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Formation deadline cannot be in the past.")
        return value
    
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