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