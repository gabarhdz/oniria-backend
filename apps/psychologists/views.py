from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .models import psychologist, university, forms, questions, answer, PsychologistProfile
from .serializers import PsychologistSerializer, UniversitySerializer, FormSerializer, QuestionSerializer, AnswerSerializer
from services.splitPDF.splitPDF import splitPDF
# Create your views here.

class AllPsychologists(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        Psychologist = psychologist.objects.all()
        serializer = PsychologistSerializer(Psychologist, many=True)
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
    
class AiTraining(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        splitter = splitPDF()
        splitter(data["pdfFile"])
        return Response({"message": "PDF procesado y datos almacenados correctamente."}, status=200)

class AllForms(APIView):
    """
    Permite listar todos los formularios y crear uno nuevo.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        forms_qs = forms.objects.all()
        serializer = FormSerializer(forms_qs, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = FormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class FormDetail(APIView):
    """
    Permite recuperar los detalles de un formulario específico.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        serializer = FormSerializer(form_obj)
        return Response(serializer.data)

class AllQuestions(APIView):
    """
    Permite listar todas las preguntas y crear una nueva.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        questions_qs = questions.objects.all()
        serializer = QuestionSerializer(questions_qs, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class CreateAnswer(APIView):
    """
    Permite enviar una respuesta para una pregunta asociada a un test.
    Valida que el valor se encuentre en la escala numérica (1-10).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class UploadProfilePic(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Endpoint para subir y procesar una imagen de perfil.
        """
        user = request.user
        uploaded_file = request.FILES.get('profile_pic')

        if not uploaded_file:
            return Response({"error": "No se proporcionó ninguna imagen."}, status=400)

        # Obtener o crear el perfil del psicólogo
        profile, created = PsychologistProfile.objects.get_or_create(user=user)

        # Procesar y guardar la imagen
        profile.save_profile_pic(uploaded_file)

        return Response({"message": "Imagen de perfil subida y procesada correctamente."}, status=200)


