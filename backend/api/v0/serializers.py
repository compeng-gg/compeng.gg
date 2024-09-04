from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

from rest_framework import serializers

class UserSocialAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSocialAuth
        fields = ['provider', 'uid']

class UserSerializer(serializers.ModelSerializer):

    social_auth = UserSocialAuthSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'social_auth']
