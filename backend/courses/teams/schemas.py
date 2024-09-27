from rest_framework import serializers
import courses.models as db

class JoinTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)

class ApproveTeamMemberRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)
    user_id = serializers.IntegerField(required=True)
        
class LeaveTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)

class DeleteTeamRequestSerializer(serializers.Serializer):
    team_id = serializers.UUIDField(required=True)