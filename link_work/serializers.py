from rest_framework import serializers
from .models import CustomUser
#rom django.contrib.auth import User
from django.core.exceptions import ValidationError


from django.contrib.auth import get_user_model

# Get the custom user model if it is set in settings.py
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Use CustomUser.objects.create_user to create the user
        return CustomUser.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
