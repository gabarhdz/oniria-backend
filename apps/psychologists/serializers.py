# serializers.py generado autom�ticamente
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import psychologist, university
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name','profile_pic']

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = university
        fields = ['id', 'name']

class PsychologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    
    class Meta:
        model = psychologist
        fields = ['user', 'university', 'description', 'startDate']