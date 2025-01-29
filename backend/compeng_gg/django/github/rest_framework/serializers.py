from rest_framework import serializers

class DeliverySerializer(serializers.Serializer):
    payload = serializers.JSONField()
