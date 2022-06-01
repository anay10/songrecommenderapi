from dataclasses import fields
from lib2to3.pgen2.tokenize import TokenError
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
#smart_str, force_str, smart_bytes are to ensure correct formatting of the data
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields=['email','username','password']

    def validate(self, attrs):
        email=attrs.get('email', '')#(____, fall back value)
        username=attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('Username should contain only alphanumeric characters')
        return attrs


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)    


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)

    class Meta:
        model=User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255, min_length = 3)
    password = serializers.CharField(max_length = 68, min_length = 6, write_only = True)
    username = serializers.CharField(max_length = 255, min_length = 3, read_only = True)
    tokens = serializers.SerializerMethodField()#we can pass name of out function but this will look for get_tokens

    def get_tokens(self, obj):
        user = User.objects.get(email = obj['email'])

        return {
            "access" : user.tokens()['access'],
            "refresh" : user.tokens()['refresh']
        }

    class Meta:
        model=User
        fields=['email', 'password', 'username', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        #check if credentials are correct
        if not user:
            raise AuthenticationFailed('Invalid credentials! Try again')
        #check if user is active
        if not user.is_active:
            raise AuthenticationFailed('Account diabled! Contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')


        return {
            'email':user.email,
            'username':user.username,
            'tokens':user.tokens()
        }

class RequestPasswordResetEmailSerializer(serializers.Serializer):
    #define the fields
    email = serializers.EmailField(min_length = 2)

    class Meta:
        fields = ['email']       

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            #force_str is used to get human readable string
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            print(user)

            #check if token was not used before
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()
            return (user)    
        except Exception as e:
            print("hello")
            raise AuthenticationFailed('The reset link is invalid', 401)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token' : ('token has expired or is invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')

        return super().save(**kwargs)