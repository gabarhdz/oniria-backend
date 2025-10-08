import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.users.models import User
from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer para manejar notificaciones en tiempo real
    """
    
    async def connect(self):
        """
        Conectar el WebSocket y unirse al grupo del usuario
        """
        # Obtener el usuario de la query string o headers
        self.user = self.scope.get('user')
        
        if self.user and self.user.is_authenticated:
            self.user_id = str(self.user.id)
            self.room_group_name = f'user_{self.user_id}'
            
            # Unirse al grupo del usuario
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Enviar notificaciones no leídas al conectar
            unread_notifications = await self.get_unread_notifications()
            await self.send(text_data=json.dumps({
                'type': 'initial_notifications',
                'notifications': unread_notifications,
                'count': len(unread_notifications)
            }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """
        Desconectar y salir del grupo
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Recibir mensajes del cliente
        """
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'mark_as_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_as_read(notification_id)
                
                await self.send(text_data=json.dumps({
                    'type': 'mark_read_success',
                    'notification_id': notification_id
                }))
            
            elif action == 'mark_all_as_read':
                await self.mark_all_as_read()
                
                await self.send(text_data=json.dumps({
                    'type': 'mark_all_read_success'
                }))
            
            elif action == 'get_unread_count':
                count = await self.get_unread_count()
                
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': count
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def notification_message(self, event):
        """
        Enviar notificación al cliente
        """
        notification = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification
        }))
    
    @database_sync_to_async
    def get_unread_notifications(self):
        """
        Obtener notificaciones no leídas del usuario
        """
        notifications = Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).order_by('-created_at')[:20]
        
        return [notif.to_dict() for notif in notifications]
    
    @database_sync_to_async
    def get_unread_count(self):
        """
        Obtener cantidad de notificaciones no leídas
        """
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """
        Marcar una notificación como leída
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
        except Notification.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_all_as_read(self):
        """
        Marcar todas las notificaciones como leídas
        """
        Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).update(is_read=True)