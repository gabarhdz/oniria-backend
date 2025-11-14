from django.db import models
from django.contrib.auth.models import AbstractUser
from services.imageHandler.imageHandler import ImageHandler  # Cambiado a importación absoluta
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField(blank=True, null=True, max_length=15000)
    profile_pic_base64 = models.TextField(blank=True, null=True)  # Campo para guardar la imagen en base64
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

    def save_profile_pic(self, uploaded_file):
        """
        Procesa y guarda la imagen de perfil en base64.
        """
        handler = ImageHandler(base_dir='users')  # Directorio temporal para usuarios
        self.profile_pic_base64 = handler.process_image(self, uploaded_file)
        self.save()

    def __str__(self):
        return self.username

class UserVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"