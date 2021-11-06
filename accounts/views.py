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
from accounts.decorators import *
from accounts.models import AdminType, User
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
    @unauthenticated_user
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
            # absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
            absurl = 'http://localhost:3000/email-verify/'+str(token)

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
            return response_bad_request({"username": "Username or Password is incorrect. Try again.", "account": "If you sure that entered account is correct, your account maybe have been looked by admin!"})


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

    @login_required
    def get(self, request):
        user = request.user
        return response_ok(ProfilePageNoPasswordSerializer(user, context=self.get_serializer_context()).data)

    @login_required
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

        if data.get('gender', '') != '':
            if str(data['gender']) not in ['Male','Female','Unknown']:
                return response_bad_request({'gender':'Unvalid data! Gender must be Male, Female or Unknown'})
            user.gender = data['gender']
        
        if data.get('date_of_birth', '') != '':
            import datetime
            date_of_birth = data['date_of_birth']
            format = "%Y-%m-%d"
            try:
                datetime.datetime.strptime(date_of_birth, format)
            except ValueError:
                return response_bad_request({'date_of_birth': 'This is the incorrect date string format. It should be YYYY-MM-DD'})
            user.date_of_birth = data['date_of_birth']
        
        if data.get("profile_pic", '') != '':
            if ImageExtensionValidator.validate(str(data["profile_pic"])):
                user.reset_profile_pic()
                user.profile_pic = data["profile_pic"]
            else:
                return response_bad_request({"profile_pic": "The file must have an image extension of .jpg, .jpeg or .png"})
        user.save()

        return response_ok(ProfilePageNoPasswordSerializer(user, context=self.get_serializer_context()).data)


class ProfilePageAPI(APIView):
    @admin_required
    def get(self, request, id):
        if not User.objects.filter(id=id).exists():
            return response_not_found(f"User with id={id} could not be found.")
        return response_ok(ProfilePageNoPasswordSerializer(User.objects.get(id=id)).data)


class LogoutAPI(APIView):
    @login_required
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return response_no_content("User logout.")


class ChangePasswordAPI(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer

    @login_required
    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = data.get('old_password', '')

            if not user.check_password(old_password):
                return response_bad_request({"old_password":"Your old password was entered incorrectly. Please enter it again."})

            if data.get('new_password1', '') != '' and data.get('new_password1', '') == data.get('new_password2', ''):
                user = serializer.save()
            # create a new token
                if hasattr(user, 'auth_token'):
                    user.auth_token.delete()
                token, created = Token.objects.get_or_create(user=user)
            # return new token
                return response_ok({'token': token.key, 'noti': 'success!'})
            return response_bad_request({"entered_password":"The two password fields didn't match."})
        return response_bad_request({"entered_password":"Password is not valid. The password length must be more than 6 with letters and numbers."})


class UserAPI(APIView):
    @admin_required
    def get(self, request):
        user = User.objects.all()
        #user = auto_apply(user, request)
        user_sdata = UserSerializer(user, many=True).data

        return response_ok(user_sdata)


class UserDetailAPI(APIView):
    @admin_required
    def get(self, request, id):
        """
        Get specific user
        """
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return response_not_found(f"User with id={id} could not be found.")
        return response_ok(UserSerializer(user).data)

    @admin_required
    def put(self, request, id):
        """
        Update a specific user
        """
        data = request.data
        UPDATE_FIELDS = ["is_active", "admin_type"]
        for field in UPDATE_FIELDS:
            data[field] = data.get(field, '')

        # Try validate
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return response_bad_request("User does not exist")

        if data["admin_type"] != '':
            if data["admin_type"] not in AdminType.TYPE:
                return response_bad_request("admin_type \'{}\' is not valid.".format(data["admin_type"]))
            user.admin_type = data["admin_type"]

        if data["is_active"] != '':
            if data["is_active"] not in ['true', 'false']:
                return response_bad_request("is_active '{}' should be either 'true' or 'false'.".format(data["is_active"]))
            if data["is_active"] == 'true':
                user.is_active = True
            else:
                user.is_active = False

        user.save()

        return response_ok(UserSerializer(user).data)
