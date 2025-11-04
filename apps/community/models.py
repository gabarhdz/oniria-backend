from django.db import models
import uuid
from apps.users.models import User
from services.imageHandler.imageHandler import ImageHandler  # Importamos el manejador de imágenes

# Create your models here.

class Community(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for the post
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField(max_length=450, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_image_base64 = models.TextField(blank=True, null=True)  # Campo para guardar la imagen en base64
    users = models.ManyToManyField(User, related_name='communities', blank=True)  # Users who are members of the community
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_communities', null=True, blank=True)  # Owner of the community

    def save_profile_image(self, uploaded_file):
        """
        Procesa y guarda la imagen de perfil en base64.
        """
        handler = ImageHandler(base_dir='communities')
        self.profile_image_base64 = handler.process_image(self, uploaded_file)
        self.save()

    def __str__(self):
        return f"Comunidad: {self.name}"


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique identifier for the post
    title = models.CharField(max_length=50, null=False, blank=False)
    text = models.TextField(max_length=2500, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Users who liked the post
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)  # Users who disliked the post

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_base64 = models.TextField(blank=True, null=True)  # Campo para guardar la imagen en base64

    def save_image(self, uploaded_file):
        """
        Procesa y guarda la imagen del post en base64.
        """
        handler = ImageHandler(base_dir='posts')
        self.image_base64 = handler.process_image(self, uploaded_file)
        self.save()

    def __str__(self):
        return f"Imagen de {self.post.title}"