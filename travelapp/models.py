from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.   
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group, Permission
from authentication.models import CustomUser


# class Hotel_details(models.Model):
#     package=models.ForeignKey(CustomisedPackage,on_delete=models.CASCADE,null=True,blank=True)
#     hotel_details=models.JSONField(null=True,blank=True)
#     number_of_people=models.IntegerField(null=True,blank=True)


class TempTokenModel(models.Model):
    email = models.CharField(max_length=50)
    token = models.CharField(max_length=16)

    def __str__(self):
        return self.email + " : " + self.token
