from django.db import models
from services.modelServices.generate_id import generate_id
from apps.users.models import User
from apps.community.models import Community, Post

class Notification(models.Model):
    """
    Modelo para notificaciones en tiempo real
    """
    NOTIFICATION_TYPES = (
        ('new_post', 'Nuevo Post en Comunidad'),
        ('post_reply', 'Respuesta a tu Post'),
        ('post_like', 'Like en tu Post'),
        ('community_join', 'Nuevo Miembro en Comunidad'),
        ('mention', 'Mención en Post'),
        ('system', 'Notificación del Sistema'),
    )

    id = models.CharField(
        max_length=20, 
        primary_key=True, 
        default=generate_id(), 
        editable=False
    )
    
    # Usuario que recibe la notificación
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    
    # Usuario que genera la notificación (puede ser None para sistema)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    
    # Tipo de notificación
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES
    )
    
    # Título y mensaje
    title = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    
    # Referencias opcionales
    community = models.ForeignKey(
        Community, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    
    # URL de redirección
    redirect_url = models.CharField(max_length=500, blank=True, null=True)
    
    # Estado
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} para {self.recipient.username}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save()
    
    def to_dict(self):
        """Convertir a diccionario para enviar por WebSocket"""
        return {
            'id': self.id,
            'type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'sender': {
                'id': self.sender.id,
                'username': self.sender.username,
                'profile_pic': self.sender.profile_pic.url if self.sender and self.sender.profile_pic else None,
            } if self.sender else None,
            'community': {
                'id': self.community.id,
                'name': self.community.name,
            } if self.community else None,
            'post': {
                'id': self.post.id,
                'title': self.post.title,
            } if self.post else None,
            'redirect_url': self.redirect_url,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
        }