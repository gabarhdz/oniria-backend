# apps/users/views.py
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserSerializer


class getAllUsers(APIView):
    permission_classes = [AllowAny]  # Cambiado para permitir acceso
    """
    A viewset for viewing and editing user instances.
    """
    def get(self, request, *args, **kwargs):
        """
        Retrieve all user instances.
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """
        Create a new user instance.
        """
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class getSpecificUser(APIView):
    permission_classes = [IsAuthenticated]
    """
    A viewset for viewing and editing user instances.
    """
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
        
        # Verificar que el usuario solo pueda editar su propio perfil
        if request.user != user:
            return Response(
                {'error': 'No tienes permisos para editar este perfil'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """
        Actualización parcial del usuario actual
        """
        return self.put(request, *args, **kwargs)