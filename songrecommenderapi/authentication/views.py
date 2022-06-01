from logging import raiseExceptions
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer, RequestPasswordResetEmailSerializer, SetNewPasswordSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
#smart_str, force_str, smart_bytes are to ensure correct formatting of the data
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util

# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer, )

    #for handling this post request made by user
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)#run to validate data, runs the validate method
        serializer.save()#runs the create method
        user_data = serializer.data#once user is saved we can access it using serializer

        user = User.objects.get(email=user_data['email'])#get user using email
        token = RefreshToken.for_user(user).access_token#create refresh token for user
        #token can be of 2 types, refresh and access
        #here we have stores access token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl='http://'+current_site+relativeLink+"?token="+str(token)

        email_body = 'Hi '+user.username+' Use link below to verify your email \n'+absurl
        data = {'email_body':email_body, 'to_email':user.email,'email_subject':'Verify your email'}

        Util.send_email(data)

        #tell user that user is created
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        #token is created using user so we can decode it using user
        #secret key in settings.py is used to encode the tokens
        try:
            print(settings.SECRET_KEY)
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            #user is verified so change the verify property
            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response({'email':'Sucessfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            #handle case where token has expired
            return Response({'error':'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            #handle case where user has tampered with token
            return Response({'error':'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        data = {'request' : request, 'data' : request.data}
        serialzer = self.serializer_class(data=data)
        email = request.data['email']
        
        #----------------------------------------------------
        if User.objects.filter(email=email).exists:
        #send email containing reset password token
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))#encode uid of the user
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request = request).domain
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64':uidb64, 'token':token})
            absurl='http://' + current_site + relativeLink

            email_body = 'Hello\nUse link below to reset your password \n'+absurl
            data = {'email_body':email_body, 'to_email':user.email,'email_subject':'Reset your password'}

            Util.send_email(data)
        #----------------------------------------------------


        return Response({'success' : 'We have sent you a link on your email address to reset your password'}, status=status.HTTP_200_OK)



class PasswordTokenCheckAPI(generics.GenericAPIView):
    #when user clicks the reset password link in the browser, it has to handle
    #get request so here we handle get request

    #used dummy serializer
    serializer_class = RequestPasswordResetEmailSerializer

    def get(self, request, uidb64, token):
        
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            #check whether user has already used the token
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error' : 'Token is not valid anymore please request new token'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"success":True, "message":"Credentials Valid", "uidb64":uidb64, "token":token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            #handle error where user has tampered with our link
            return Response({'error' : 'Token is not valid anymore please request new token'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    #since we are editing user, we use patch method here
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception = True)
        return Response({"success":True, "message":"Password reset successful"}, status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)