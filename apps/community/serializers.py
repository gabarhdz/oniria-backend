from rest_framework import serializers
from .models import Community, Post
from apps.users.serializers import UserSerializer


class CommunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    users = UserSerializer(many=True,read_only=True)
    class Meta:
        model = Community
        fields = [ 'id', 'name', 'description', 'profile_image','created_at','users']


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
        # Para GET: devolver comunidad serializada
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
