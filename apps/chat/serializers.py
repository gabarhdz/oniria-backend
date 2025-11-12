# apps/chat/serializers.py
from rest_framework import serializers
from .models import Conversation, Message
from apps.users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'content',
            'created_at', 'is_read', 'read_at', 'is_system_message'
        ]
        read_only_fields = ['id', 'created_at', 'sender']


class ConversationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    psychologist = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'psychologist', 'created_at',
            'updated_at', 'is_active', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """Obtener el último mensaje de la conversación"""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'id': str(last_message.id),
                'content': last_message.content,
                'sender_id': str(last_message.sender.id),
                'created_at': last_message.created_at.isoformat(),
                'is_read': last_message.is_read
            }
        return None
    
    def get_unread_count(self, obj):
        """Contar mensajes no leídos para el usuario actual"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        
        # Contar mensajes no leídos que no son del usuario actual
        return obj.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer para crear una nueva conversación"""
    psychologist_id = serializers.UUIDField()
    initial_message = serializers.CharField(max_length=5000, required=False)
    
    def validate_psychologist_id(self, value):
        """Validar que el psicólogo existe y es psicólogo"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            psychologist = User.objects.get(id=value)
            if not psychologist.is_psychologist:
                raise serializers.ValidationError(
                    "El usuario seleccionado no es un psicólogo"
                )
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Psicólogo no encontrado")