from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import psychologist
from .serializers import PsychologistSerializer
# Create your views here.

class AllPsychologists(APIView):
    def get(self, request, *args, **kwargs):
        Psychologist = psychologist.objects.all()
        serializer = PsychologistSerializer(Psychologist,many=True)
        return Response(serializer.data) 
