from rest_framework import serializers


class UserPublicSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    email = serializers.CharField()
    role = serializers.CharField()
    avatar_url = serializers.CharField(allow_null=True, required=False)
    bio = serializers.CharField(allow_null=True, required=False)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
