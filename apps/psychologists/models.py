from django.db import models
from django.contrib.auth.models import AbstractUser
from services.modelServices.generate_id import generate_id
from django.conf import settings
import random
import string

# Create your models here.

class emotion(models.Model):
    name = models.CharField(null=False,max_length=100)

class university(models.Model):
    name = models.CharField(null=False,max_length=100)

    




class psychologist(models.Model):
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    primary_key=True,
    related_name='psychologist_profile',      # <- aquí defines el nombre único
    related_query_name='psychologist_profiles')  # <- aquí defines el nombre único
    university = models.ForeignKey(university,on_delete=models.SET_NULL,null=True,blank=True)
    description = models.TextField(blank=True, null=True,max_length=15000)  # Optional description field
    startDate = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.user.username