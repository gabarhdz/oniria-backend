from django.db import models
from services.modelServices.generate_id import generate_id
from services.UploadProfilePic.UploadProfilePic import UploadProfilePic
from django.contrib.auth.models import AbstractUser
# Create your models here.
import os
#from apps.psychologists.models import psychologist

id_generator = generate_id() 

# In apps/users/models.py
class SleepState(models.Model):
    problems = models.TextField(max_length=500, blank=False, null=False)
    startDate = models.DateTimeField(auto_now_add=True)
    endDate = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # Fix the string representation to use fields that actually exist
        return f"Sleep State - {self.startDate}"
class User(AbstractUser):
    id = models.CharField(max_length=20, primary_key=True, default=id_generator, editable=False)  # Unique identifier for the user
    description = models.TextField(blank=True, null=True,max_length=15000)  # Optional description field
    profile_pic = models.ImageField(upload_to=UploadProfilePic(base_dir='accounts'),blank=True,null=True)
    SleepState = models.ForeignKey(SleepState, on_delete=models.SET_NULL,null=True, blank=True)
    email = models.CharField(max_length=60,unique=True,null=False, blank=False)
    is_psychologist = models.BooleanField(default=False,help_text="Marca si el usuario es un psicólogo certificado.")  
    def save(self, *args, **kwargs):
        if not self.id:
            new_id = id_generator()  # Usamos la instancia callable para generar el ID
            # Ensure the ID is unique
            while User.objects.filter(id=new_id).exists():
                new_id = id_generator()  # Generamos un nuevo ID si ya existe uno igual
            self.id = new_id
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username

