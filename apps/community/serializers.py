from rest_framework import serializers
from .models import Community
from apps.users.serializers import UserSerializer

class CommunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    users = UserSerializer(many=True,read_only=True)
    class Meta:
        model = Community
        fields = [ 'id', 'name', 'description', 'profile_image','created_at','users']

