from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import make_password
from django.db import transaction, IntegrityError
from rest_framework.settings import import_from_string
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import serializers, status, generics, status, views, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from kanben import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.serializers import *
from utils.make_response import *
from kanben.settings import *
from .utils import Util

# Create your views here.

import datetime
import pytz


def utc_now():
    utc_now = datetime.datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    return utc_now


class ImageExtensionValidator:
    VALID_IMAGE_EXTENSIONS = [
        ".jpg", ".jpeg", ".png", ".gif",
    ]

    def validate(path, extension_list=VALID_IMAGE_EXTENSIONS):
        return any([path.endswith(e) for e in extension_list])


class RegisterAPI(APIView):
    '''
    For Registering a new account
    '''
    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        username = data.get("username", '')
        email = data.get("email", '')
        password = data.get("password", '')
        if username != '' and username.isalnum():
            if User.objects.filter(username=data["username"].lower()).exists():
                return response_bad_request({"username": "This username already exists"})
        else:
            return response_bad_request({"username": "Username can only contain alphanumeric characters."})
        if email != '':
            try:
                validate_email(email)
                if User.objects.filter(email=email.lower()).exists():
                    return response_bad_request({"email": "This email already exists"})
            except ValidationError:
                return response_bad_request({"email": "This email is invalid"})
        else:
            return response_bad_request({"email": "This field is required."})
        if password != '' and 6 <= len(password) <= 32:
            serializer.is_valid()
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=data['email'])
            print(user.username)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            email_body = 'Hi '+user.username + \
                ' Use the link below to verify your email \n' + absurl
            send_data = {'email_body': email_body, 'to_email': user.email,
                         'email_subject': 'Verify your email'}
            print(send_data)
            Util.send_email(send_data)
            return response_created(user_data)

        return response_bad_request({"password": "The password length must be more than 6 with letters and numbers."})


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = [SessionAuthentication]

    # @unauthenticated_user # not required to logout, refresh token
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if request.data['username'].strip() == "":
            return response_bad_request({"username": "This field is required."})
        if request.data['password'].strip() == "":
            return response_bad_request({"password": "This field is required."})

        if serializer.is_valid():
            user = serializer.validated_data

            if request.user.is_authenticated:
                if user != request.user:
                    return response_bad_request("Cannot login as another user if you are already logged on")
                request.user.auth_token.delete()
                logout(request)

            try:
                if user.is_verified == False:
                    return response_bad_request("Your account hasn't been verified yet! Please check your email for verification link!")
                login(request, user)
                # print(user.is_verified)
            except FileNotFoundError:
                user.reset_profile_pic()
                login(request, user)

            user_data = User.objects.get(username=request.data['username'])
            try:  # Delete the Token if it exists
                token = Token.objects.get(user=user_data)
                token.delete()
            except Token.DoesNotExist:
                pass
            except:
                raise
            # Recreate Token for the user who is logging in
            token = Token.objects.create(user=user_data)

            return response_ok({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": str(token),
                "TTL": int(TOKEN_EXPIRE_AFTER_SECONDS - (utc_now() - token.created).total_seconds()+0.5),
            })
        else:
            return response_bad_request({"username": "Username or Password is incorrect. Try again."})


class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        print('This is token', token)
        try:
            payload = jwt.decode(jwt=str(token), key=settings.SECRET_KEY, algorithms=['HS256'])
            print(payload['user_id'])
            user = User.objects.get(id=payload['user_id'])
            print(user.username)
            if user.is_verified == False:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class OwnProfilePageAPI(generics.GenericAPIView):
    serializer_class = ProfilePageNoPasswordSerializer

    # @login_required
    def get(self, request):
        user = request.user
        return response_ok(ProfilePageNoPasswordSerializer(user, context=self.get_serializer_context()).data)

    # @login_required
    def put(self, request):
        user = request.user
        data = request.data

        if data.get("username", '') != '':
            if User.objects.filter(username=data["username"].lower()).exclude(id=user.id).exists():
                return response_bad_request({"username": "This username already exists"})
            user.username = data["username"].lower()

        if data.get("password", '') != '':
            return response_bad_request("Please use profile/change-password API for password changing")

        if data.get("email", '') != '':
            if User.objects.filter(email=data["email"].lower()).exclude(id=user.id).exists():
                return response_bad_request({"email": "This email already exists"})
            user.email = data["email"].lower()

        if data.get("profile_pic", '') != '':
            if ImageExtensionValidator.validate(str(data["profile_pic"])):
                user.reset_profile_pic()
                user.profile_pic = data["profile_pic"]
            else:
                return response_bad_request({"profile_pic": "The file must have an image extension of .jpg, .jpeg or .png"})
        user.save()

        return response_ok(ProfilePageNoPasswordSerializer(user, context=self.get_serializer_context()).data)


class LogoutAPI(APIView):
    # @login_required
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return response_no_content("User logout.")
