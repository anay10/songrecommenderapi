from os import access
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, 
BaseUserManager, PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.


class UserManager(BaseUserManager):#maintains which querysets we can run
    def create_user(self,username,email,password=None):
        if username is None:
            raise TypeError('Users should have a username')

        if email is None:
            raise TypeError('Users should have a username')

        #define how user is created
        user = self.model(username=username, email=self.normalize_email(email))        
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username,email,password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username,email,password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username=models.CharField(max_length=255, unique=True, db_index=True)
    email=models.EmailField(max_length=255, unique=True, db_index=True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] #list of necessary fields

    objects = UserManager()

    #define hoe these types of objects must be processed
    def __str__(self):
        return self.email

    def tokens(self):#this method gives tokens to this particular user
        refresh=RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }    
