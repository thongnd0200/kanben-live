from django.conf import settings
from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import authenticate, login, logout, password_validation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                "The username should only contain alphanumeric characters")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class ProfilePageSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(default='profile1.png')

    class Meta:
        model = User
        fields = '__all__'


class ProfilePageNoPasswordSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(default='profile1.png')
    

    class Meta:
        model = User
        exclude = ('password',)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(
        max_length=128, write_only=True, required=True)

    # def validate_new_password1(self, value):
    #     validate_password(value)
    #     return value

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user