from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .permissions import IsOwnerOrReadOnly, IsCommunityOwnerOrReadOnly
from .models import Community, Post
from .serializers import CommunitySerializer, PostSerializer
import json
# Create your views here.

class Communities(APIView):
    permission_classes = [IsCommunityOwnerOrReadOnly]
    
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
        serializer = CommunitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Asignar el usuario actual como propietario
            community = serializer.save(owner=request.user)
            # Agregar automáticamente al creador como miembro
            community.users.add(request.user)
            return Response(CommunitySerializer(community, context={'request': request}).data, status=201)
        return Response(serializer.errors, status=400)    
    

class SimilarCommunities(APIView):
    def get(self, request, name, *args, **kwargs):
        """
        Retrieve similar communities based on a given community name.
        """
        try:
            similar_communities = Community.objects.filter(name__icontains=name)
            serializer = CommunitySerializer(similar_communities, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({"error": "An error occurred while retrieving similar communities."}, status=500)
        

class DetailedCommunity(APIView):
    permission_classes = [IsCommunityOwnerOrReadOnly]
    
    def get(self, request, pk, *args, **kwargs):
        try:    
            community = Community.objects.get(pk=pk)
            serializer = CommunitySerializer(community, context={'request': request})
            print(serializer.data)
            return Response(serializer.data, status=200)
        except Community.DoesNotExist:
            return Response({"error": "Community not found."}, status=404)
        except Exception as e:
            print(f"Error occurred: {e}")
            return Response({"error": "An error occurred while retrieving the community."}, status=500)
    
    def put(self, request, pk, *args, **kwargs):
        try:
            community = Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return Response({"error": "Community not found."}, status=404)
        
        # Verificar permisos
        self.check_object_permissions(request, community)
        
        serializer = CommunitySerializer(community, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            community = Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return Response({"error": "Community not found."}, status=404)
        
        # Verificar permisos
        self.check_object_permissions(request, community)
        
        community.delete()
        return Response({"message": "Community deleted successfully."}, status=204)


class FilterPostByCommunity(APIView):
    def get(self, request, community, *args, **kwargs):
        try:
            posts = Post.objects.filter(community__id=community)
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"Error": f"An error just occurred: {e}"}, status=500)


class Posts(APIView):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('created_at')
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
    
    def put(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error":"Post no encontrado"}, status=404)
        
        self.check_object_permissions(request, post)
        
        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error":"Post no encontrado"}, status=404)
        
        self.check_object_permissions(request, post)  # ← LÍNEA CLAVE
        post.delete()
        return Response({"message":"Post eliminado exitosamente"}, status=204)


class GiveLikes(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)
        
        # Remover de dislikes si existe
        if user in post.dislikes.all():
            post.dislikes.remove(user)
        
        # Toggle like
        if user in post.likes.all():
            post.likes.remove(user)
            message = "Like removido exitosamente"
        else:
            post.likes.add(user)
            message = "Has dado like exitosamente"
        
        post.save()
        return Response({"message": message}, status=200)


class GiveDislikes(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=404)
        
        # Remover de likes si existe
        if user in post.likes.all():
            post.likes.remove(user)
        
        # Toggle dislike
        if user in post.dislikes.all():
            post.dislikes.remove(user)
            message = "Dislike removido exitosamente"
        else:
            post.dislikes.add(user)
            message = "Has dado dislike exitosamente"
        
        post.save()
        return Response({"message": message}, status=200)
    

class JoinCommunities(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            community = Community.objects.get(pk=pk)
        except Community.DoesNotExist:
            return Response({"error": "Community not found"}, status=404)
        
        # Toggle membership
        if user in community.users.all():
            community.users.remove(user)
            message = f"Has salido de la comunidad {community.name}"
        else:
            community.users.add(user)
            message = f"Ahora eres parte de la comunidad {community.name}"
        
        community.save()
        return Response({"message": message}, status=200)