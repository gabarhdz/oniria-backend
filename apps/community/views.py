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
        serializer = CommunitySerializer(communities, many=True, context={'request': request})
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
    

class SimilarCommunities(APIView):
    def get(self,request,name,  *args, **kwargs):
        """
        Retrieve similar communities based on a given community ID.
        """
        try:
            similar_communities = Community.objects.filter(name__contains=name)
            serializer = CommunitySerializer(similar_communities, many=True, context={'request': request})
            print("Data is:")
            print(serializer.data)
            return Response(serializer.data,status=200)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({"error": "An error occurred while retrieving similar communities."}, status=500)
        
class DetailedCommunity(APIView):
    def get(self,request,pk,*args,**kwargs):
        try:    
            community = Community.objects.get(pk=pk)
            serializer = CommunitySerializer(community, context={'request': request})
            print(serializer.data)
            return Response(serializer.data, status=200)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({"error": "An error occurred while retrieving similar communities."}, status=500)
    def put(self,request,pk,*args,**kwargs):
        updated_community = Community.objects.filter(pk=pk)
        communities_serializer = CommunitySerializer(updated_community,data=request.data)
        if communities_serializer.is_valid():
            communities_serializer.save()
            return(communities_serializer.data)
        return(communities_serializer.errors)