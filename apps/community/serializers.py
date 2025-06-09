from rest_framework import serializers
from .models import Community


class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = [ 'id', 'name', 'description', 'profile_image','created_at']
    