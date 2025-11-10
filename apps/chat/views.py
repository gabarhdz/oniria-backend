# apps/chat/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    ConversationCreateSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar conversaciones
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """
        Obtener conversaciones del usuario actual
        """
        user = self.request.user
        return Conversation.objects.filter(
            Q(user=user) | Q(psychologist=user)
        ).select_related('user', 'psychologist').prefetch_related('messages')
    
    def create(self, request, *args, **kwargs):
        """
        Crear o obtener conversación existente con un psicólogo
        """
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        psychologist_id = serializer.validated_data['psychologist_id']
        initial_message = serializer.validated_data.get('initial_message')
        
        psychologist = get_object_or_404(User, id=psychologist_id)
        
        # Verificar que el usuario no sea el psicólogo
        if request.user == psychologist:
            return Response(
                {'error': 'No puedes iniciar una conversación contigo mismo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener o crear conversación
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            psychologist=psychologist,
            defaults={'is_active': True}
        )
        
        # Si se proporcionó un mensaje inicial, crearlo
        if initial_message and created:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message
            )
        
        serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Obtener todos los mensajes de una conversación
        """
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('created_at')
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marcar todos los mensajes de la conversación como leídos
        """
        conversation = self.get_object()
        
        # Marcar mensajes como leídos (excepto los del usuario actual)
        unread_messages = conversation.messages.filter(
            is_read=False
        ).exclude(sender=request.user)
        
        count = unread_messages.update(is_read=True)
        
        return Response({
            'message': f'{count} mensajes marcados como leídos',
            'count': count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Obtener total de mensajes no leídos del usuario
        """
        user = request.user
        conversations = Conversation.objects.filter(
            Q(user=user) | Q(psychologist=user)
        )
        
        total_unread = 0
        for conversation in conversations:
            unread = conversation.messages.filter(
                is_read=False
            ).exclude(sender=user).count()
            total_unread += unread
        
        return Response({'unread_count': total_unread})


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver mensajes (solo lectura)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """
        Obtener mensajes de las conversaciones del usuario
        """
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__user=user) | Q(conversation__psychologist=user)
        ).select_related('sender', 'conversation').order_by('-created_at')