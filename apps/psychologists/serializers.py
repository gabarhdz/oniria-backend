# serializers.py generado autom�ticamente
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import psychologist
User = get_user_model()

class PsychologistSerializer(serializers.Serializer):
    user = User
    class Meta:
        model = psychologist
        fields = ["id","user","university","description","startDate"]