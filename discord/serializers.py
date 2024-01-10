from rest_framework import serializers

from social_django.models import UserSocialAuth

class UserSocialAuthSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = UserSocialAuth
        fields = ['user', 'uid']
