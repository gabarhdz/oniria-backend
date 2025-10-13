from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSerializer
from apps.community.serializers import CommunitySerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    community = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'sender',
            'community',
            'post',
            'redirect_url',
            'is_read',
            'created_at',
            'read_at'
        ]
    
    def get_community(self, obj):
        if obj.community:
            return {
                'id': obj.community.id,
                'name': obj.community.name,
                'profile_image': obj.community.profile_image.url if obj.community.profile_image else None
            }
        return None
    
    def get_post(self, obj):
        if obj.post:
            return {
                'id': obj.post.id,
                'title': obj.post.title
            }
        return None