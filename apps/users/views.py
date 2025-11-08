# apps/users/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)


class getAllUsers(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        """
        Retrieve all user instances.
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new user instance with profile picture in base64
        """
        try:
            # El serializer ahora maneja todo internamente
            serializer = UserSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                user = serializer.save()
                
                # Retornar datos del usuario creado
                response_serializer = UserSerializer(user, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al crear usuario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class getSpecificUser(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        """
        Retrieve a user instance.
        """
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk, *args, **kwargs):
        """
        Update a user instance.
        """
        user = get_object_or_404(User, pk=pk)
        
        # Verificar permisos
        if request.user != user:
            return Response(
                {'error': 'No tienes permisos para editar este perfil'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                user = serializer.save()
                response_serializer = UserSerializer(user, context={'request': request})
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al actualizar usuario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, pk, *args, **kwargs):
        """
        Partially update a user instance.
        """
        return self.put(request, pk, *args, **kwargs)


class getCurrentUser(APIView):
    """
    Vista para obtener los datos del usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Obtener datos del usuario actual
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, *args, **kwargs):
        """
        Actualizar datos del usuario actual
        """
        try:
            serializer = UserSerializer(
                request.user, 
                data=request.data, 
                partial=True, 
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = serializer.save()
                response_serializer = UserSerializer(user, context={'request': request})
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating current user: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error al actualizar usuario: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request, *args, **kwargs):
        """
        Actualización parcial del usuario actual
        """
        return self.put(request, *args, **kwargs)