# apps/community/serializers.py
from rest_framework import serializers
from .models import Community, Post
from apps.users.serializers import UserSerializer


class CommunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    users = UserSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'profile_image', 'created_at', 'users', 'owner']
    
    def get_profile_image(self, obj):
        """
        Devuelve la imagen en formato base64 con el prefijo data:image correcto
        """
        if obj.profile_image_base64:
            # Si ya tiene el prefijo data:image, devolverlo tal cual
            if obj.profile_image_base64.startswith('data:image'):
                return obj.profile_image_base64
            # Si no, agregar el prefijo
            return f"data:image/jpeg;base64,{obj.profile_image_base64}"
        return None
    
    def create(self, validated_data):
        """
        Crear comunidad y procesar imagen
        """
        # Crear comunidad
        community = Community.objects.create(**validated_data)
        
        # Procesar imagen si existe en el request
        request = self.context.get('request')
        if request and request.FILES.get('profile_image'):
            uploaded_file = request.FILES['profile_image']
            community.save_profile_image(uploaded_file)
        
        return community
    
    def update(self, instance, validated_data):
        """
        Actualizar comunidad y procesar nueva imagen si se proporciona
        """
        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Procesar nueva imagen si existe
        request = self.context.get('request')
        if request and request.FILES.get('profile_image'):
            uploaded_file = request.FILES['profile_image']
            instance.save_profile_image(uploaded_file)
        
        instance.save()
        return instance


class PostSerializer(serializers.ModelSerializer):
    community = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    likes = UserSerializer(many=True, read_only=True)
    dislikes = UserSerializer(many=True, read_only=True)
    parent_post = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'created_at', 'community', 'parent_post', 'author', 'likes', 'dislikes']

    def get_community(self, obj):
        return CommunitySerializer(obj.community, context=self.context).data

    def to_internal_value(self, data):
        request = self.context.get('request')
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            if 'community' in data:
                try:
                    community = Community.objects.get(id=data['community'])
                    data['community'] = community
                except Community.DoesNotExist:
                    raise serializers.ValidationError({'community': 'Community not found'})
        return super().to_internal_value(data)

    def get_parent_post(self, obj):
        if obj.parent_post:
            return PostSerializer(obj.parent_post, context=self.context).data
        return None