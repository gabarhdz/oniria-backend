from rest_framework import serializers
from .models import Community


class CommunitySerializer(serializers.Serializer):
    class Meta:
        model = Community
        fields = ['url', 'id', 'name', 'description', 'profile_pic','created_at']
        extra_kwargs = {
            'url': {'view_name': 'community-detail', 'lookup_field': 'pk'},
        }
    