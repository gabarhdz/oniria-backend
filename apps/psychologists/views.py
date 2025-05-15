from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import psychologist,university
from rest_framework.exceptions import NotFound
from .serializers import PsychologistSerializer,UniversitySerializer
# Create your views here.

class AllPsychologists(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        Psychologist = psychologist.objects.all()
        serializer = PsychologistSerializer(Psychologist,many=True)
        return Response(serializer.data) 
    def post(self, request, pk=None, *args, **kwargs):
        data = request.data
        user = request.user

        try:
            university_instance = university.objects.get(id=data['university'])
        except university.DoesNotExist:
            raise NotFound("Universidad no encontrada.")

        Psychologist = psychologist.objects.create(
            user=user,
            university=university_instance,
            description=data['description']
        )

        return Response({
            'user_id': Psychologist.user.id,
            'university': university_instance.name,
            'description': Psychologist.description
        }, status=201)
    

class SpecificPsychologist(APIView):
    def get(self, request, pk=None, *args, **kwargs):
        psychologist_obj = get_object_or_404(psychologist, user_id=pk)
        serializer = PsychologistSerializer(psychologist_obj)
        return Response(serializer.data)
    
    