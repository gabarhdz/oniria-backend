from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """
    GET: Listar todas las notificaciones del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:50]
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationDetailView(APIView):
    """
    GET: Obtener una notificación específica
    DELETE: Eliminar una notificación
    PATCH: Marcar como leída
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            notification.mark_as_read()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                recipient=request.user
            )
            notification.delete()
            return Response(
                {'message': 'Notificación eliminada'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notificación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class NotificationMarkAllReadView(APIView):
    """
    POST: Marcar todas las notificaciones como leídas
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} notificaciones marcadas como leídas',
            'count': updated
        })


class NotificationUnreadCountView(APIView):
    """
    GET: Obtener cantidad de notificaciones no leídas
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return Response({'unread_count': count})


class NotificationClearAllView(APIView):
    """
    DELETE: Eliminar todas las notificaciones leídas
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(
            recipient=request.user,
            is_read=True
        ).delete()
        
        return Response({
            'message': f'{deleted_count} notificaciones eliminadas',
            'count': deleted_count
        })