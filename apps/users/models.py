from django.db import models
from services.modelServices.generate_id import generate_id
from services.UploadProfilePic.UploadProfilePic import UploadProfilePic
from services.compressImages.compressImages import compressImages
from django.contrib.auth.models import AbstractUser
# Create your models here.
import os
import uuid
#from apps.psychologists.models import psychologist

id_generator = generate_id() 

# In apps/users/models.py
class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    
    description = models.TextField(blank=True, null=True, max_length=15000)
    profile_pic = models.TextField(
        blank=True, 
        null=True
    )  
    
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