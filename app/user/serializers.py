"""Serializers for the users API"""

from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializers(serializers.ModelSerializer):
    """Serializers for the users API"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'name')
        extra_kwargs = {'password':{'write_only':True, 'min_length':5}}

    def create_user(self, validated_data):
        """Create a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)