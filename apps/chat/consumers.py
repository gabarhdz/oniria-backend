# apps/chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Message, ChatNotification

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Conectar al WebSocket de chat
        """
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Obtener conversation_id de la URL
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Verificar que el usuario pertenece a esta conversación
        if not await self.user_belongs_to_conversation():
            await self.close()
            return
        
        # Unirse al grupo de la conversación
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Marcar mensajes como leídos
        await self.mark_messages_as_read()
        
        # Enviar historial reciente
        history = await self.get_recent_messages()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': history
        }))
    
    async def disconnect(self, close_code):
        """
        Desconectar del WebSocket
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Recibir mensaje del WebSocket
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'send_message':
                await self.handle_send_message(data)
            elif action == 'mark_as_read':
                await self.mark_messages_as_read()
            elif action == 'typing':
                await self.handle_typing(data)
            
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_send_message(self, data):
        """
        Manejar envío de mensaje
        """
        content = data.get('content', '').strip()
        
        if not content:
            return
        
        # Crear mensaje en la base de datos
        message = await self.create_message(content)
        
        if not message:
            return
        
        # Enviar mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': str(message.id),
                    'content': message.content,
                    'sender': {
                        'id': str(message.sender.id),
                        'username': message.sender.username,
                        'profile_pic': message.sender.profile_pic_base64
                    },
                    'created_at': message.created_at.isoformat(),
                    'is_read': message.is_read
                }
            }
        )
        
        # Crear notificación para el otro usuario
        await self.create_chat_notification(message)
    
    async def handle_typing(self, data):
        """
        Manejar indicador de escritura
        """
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def chat_message(self, event):
        """
        Recibir mensaje del grupo y enviarlo al WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def user_typing(self, event):
        """
        Recibir indicador de escritura y enviarlo al WebSocket
        """
        # No enviar al mismo usuario que está escribiendo
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    @database_sync_to_async
    def user_belongs_to_conversation(self):
        """
        Verificar que el usuario pertenece a la conversación
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return (
                conversation.user == self.user or 
                conversation.psychologist == self.user
            )
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, content):
        """
        Crear mensaje en la base de datos
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content
            )
            
            # Actualizar timestamp de la conversación
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=['updated_at'])
            
            return message
        except Exception as e:
            print(f"Error creating message: {e}")
            return None
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        """
        Marcar todos los mensajes de la conversación como leídos
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            # Marcar mensajes como leídos (excepto los del usuario actual)
            unread_messages = Message.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=self.user)
            
            unread_messages.update(
                is_read=True,
                read_at=timezone.now()
            )
            
        except Exception as e:
            print(f"Error marking messages as read: {e}")
    
    @database_sync_to_async
    def get_recent_messages(self, limit=50):
        """
        Obtener mensajes recientes de la conversación
        """
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            messages = Message.objects.filter(
                conversation=conversation
            ).select_related('sender').order_by('-created_at')[:limit]
            
            # Invertir para orden cronológico
            messages = list(reversed(messages))
            
            return [
                {
                    'id': str(msg.id),
                    'content': msg.content,
                    'sender': {
                        'id': str(msg.sender.id),
                        'username': msg.sender.username,
                        'profile_pic': msg.sender.profile_pic_base64
                    },
                    'created_at': msg.created_at.isoformat(),
                    'is_read': msg.is_read
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    @database_sync_to_async
    def create_chat_notification(self, message):
        """
        Crear notificación de nuevo mensaje
        """
        try:
            conversation = message.conversation
            
            # Determinar el destinatario (el que no es el remitente)
            recipient = (
                conversation.psychologist 
                if message.sender == conversation.user 
                else conversation.user
            )
            
            # Crear notificación
            ChatNotification.objects.create(
                recipient=recipient,
                conversation=conversation,
                message=message
            )
            
        except Exception as e:
            print(f"Error creating notification: {e}")