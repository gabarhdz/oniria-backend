from django.db import models
from services.modelServices.generate_id import generate_id
from services.UploadProfilePic.UploadProfilePic import UploadProfilePic
from services.compressImages.compressImages import compressImages
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
    id = models.CharField(
        max_length=20, 
        primary_key=True, 
        default=id_generator, 
        editable=False
    )
    description = models.TextField(blank=True, null=True, max_length=15000)
    profile_pic = models.ImageField(
        upload_to=UploadProfilePic(base_dir='accounts'),
        blank=True,
        null=True
    )
    SleepState = models.ForeignKey(
        SleepState, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )
    # CAMBIO IMPORTANTE: usar EmailField en lugar de CharField
    email = models.EmailField(
        max_length=254,  # Estándar RFC 5321
        unique=True,
        null=False,
        blank=False
    )
    is_psychologist = models.BooleanField(
        default=False,
        help_text="Marca si el usuario es un psicólogo certificado."
    )

    def save(self, *args, **kwargs):
        # Generar ID único solo si es un nuevo objeto
        if not self.pk:  # Mejor usar self.pk que self.id
            new_id = id_generator()
            # Asegurar que el ID sea único
            while User.objects.filter(id=new_id).exists():
                new_id = id_generator()
            self.id = new_id
        
        # Comprimir imagen si existe
        if self.profile_pic:
            # Solo comprimir si es un archivo nuevo o modificado
            try:
                # Guardar primero para obtener la ruta del archivo
                super().save(*args, **kwargs)
                compressor = compressImages()
                compressor(self.profile_pic.path)
                # No llamar save() nuevamente para evitar loop infinito
                return
            except Exception as e:
                # Manejar errores de compresión
                print(f"Error comprimiendo imagen: {e}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username