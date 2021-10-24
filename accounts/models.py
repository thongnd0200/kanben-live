from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from PIL import Image
import os

from django.db.models.fields import DateField

# Create your models here.


class AdminType(object):
    REGULAR_USER = 'Regular User'
    ADMIN = 'Admin'

    TYPE = [REGULAR_USER, ADMIN]


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('User should have a Username!')
        if email is None:
            raise TypeError('User should have a Email!')
        
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email=None, password=None):
            if username is None:
                raise TypeError('User should have a Username!')
            if password is None:
                raise TypeError('Password should not be None!')

            user = self.model(username=username, email=self.normalize_email(email))
            user.set_password(password)
            user.admin_type = AdminType.ADMIN
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.is_verified = True
            user.save()
            return user


class User(AbstractBaseUser, PermissionsMixin):
    TYPES_OF_GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unknown','Unknown')
    )
    
    username = models.CharField(max_length=20,unique=True, db_index=True)
    email = models.EmailField(max_length=50,null=True)
    date_of_birth = DateField(null=True)
    gender =  models.TextField(choices=TYPES_OF_GENDER)
    profile_pic = models.ImageField(default='profile1.png',null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) 
    is_verified = models.BooleanField(default=False) 
    admin_type = models.CharField(max_length=50,default=AdminType.REGULAR_USER)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    DISPLAY_FIELD = [
        "username", 
        "email", 
        "date_of_birth" ,
        "gender",
        "admin_type", 
        "is_active"
    ]

    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.profile_pic.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_pic.path)
    
    def is_admin(self):
        return self.admin_type == AdminType.ADMIN

    def reset_profile_pic(self):
        if not self.is_using_default_profile_pic():
            if os.path.exists(self.profile_pic.path):
                os.remove(self.profile_pic.path)
            self.profile_pic = User._meta.get_field('profile_pic').get_default()
            self.save()
    
    def __str__(self):
        return self.username

    def __repr__(self):
        d = {}
        for field in self.DISPLAY_FIELD:
            d[field] = getattr(self, field)
        return str(d)