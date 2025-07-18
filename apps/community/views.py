from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .permissions import IsOwnerOrReadOnly
from .models import Community, Post
from .serializers import CommunitySerializer,PostSerializer
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
    
class FilterPostByCommunity(APIView):
    def get(self, request, community, *args, **kwargs):
        try:
            posts = Post.objects.filter(community__id=community)
            serializer = PostSerializer(posts, many=True,context={'request': request})
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"Error": f"An error just occurred: {e}"}, status=500)



class Posts(APIView):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        print("Cantidad de posts:", posts.count())  # Debug
        for post in posts:
            print(post.title)  # Debug: o cualquier campo
        serializer = PostSerializer(posts, many=True, context={'request': request})
        print(serializer.data)  # Debug
        return Response(serializer.data, status=200)
    def post(self, request, *args, **kwargs):
        user = request.user
        community_id = request.data["community"]
        parent_post_id = request.data.get("parent_post")  

        # Convertir el ID a instancias reales
        community = get_object_or_404(Community, id=community_id)
        parent_post = None
        if parent_post_id:
            parent_post = get_object_or_404(Post, id=parent_post_id)

        # Crear el post a mano
        Post.objects.create(
            title=request.data["title"],
            text=request.data["text"],
            community=community,
            author=user,
            parent_post=parent_post
        )

        return Response({"message": "Post exitoso"}, status=201)

class SpecPost(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    
    def get(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error":"Post no encontrado"}, status=404)
        
        self.check_object_permissions(request, post)  # Agregar esta línea
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error":"Post no encontrado"}, status=404)
        
        self.check_object_permissions(request, post)  # ← LÍNEA CLAVE
        post.delete()
        return Response({"message":"Post eliminado exitosamente"})