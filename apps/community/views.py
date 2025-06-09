from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Community
from .serializers import CommunitySerializer
# Create your views here.
class Communities(APIView):
    def get(self, request, *args, **kwargs):
        """
        Retrieve all communities.
        """
        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
        print(serializer.data)
        return Response(serializer.data)
    def post(self, request, *args, **kwargs):
        """
        Create a new community.
        """
        serializer = CommunitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)