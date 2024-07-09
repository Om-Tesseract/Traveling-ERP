from django.db import models

from django.contrib.auth.models import (
    Group,
    AbstractUser,
    Permission,
)

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import Group, Permission
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True, blank=True, null=True)
    password = models.CharField(max_length=500, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    mobile_number = models.CharField(max_length=10, blank=True, null=True)
    address1 = models.CharField(max_length=125, blank=True, null=True)
    address2 = models.CharField(max_length=125, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, unique=True)

    roles = (
        ("Admin", "Admin"),
        ("Company", "Company"),
        ("Accountant", "Accountant"),
        ("Employee", "Employee")
    )
    role = models.CharField(max_length=50, choices=roles, default='Employee')
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser',
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'custom_user'
        verbose_name_plural = 'custom_users'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

