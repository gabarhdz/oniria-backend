from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


class getAllUsers(APIView):
    permission_classes = []
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
        
        serializer = UserSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        




class getSpecificUser(APIView):
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
    