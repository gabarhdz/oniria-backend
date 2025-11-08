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

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        try:
            # Verificar que el usuario sea psicólogo
            if not user.is_psychologist:
                return Response(
                    {"error": "El usuario debe estar marcado como psicólogo"}, 
                    status=400
                )
            
            # Verificar que no exista ya un perfil de psicólogo
            if hasattr(user, 'psychologist_profile'):
                return Response(
                    {"error": "El usuario ya tiene un perfil de psicólogo"}, 
                    status=400
                )

            # Obtener o crear la universidad por nombre
            university_name = data.get('university', '')
            if not university_name:
                return Response(
                    {"error": "La universidad es requerida"}, 
                    status=400
                )

            # Crear o obtener la universidad
            university_instance, created = university.objects.get_or_create(
                name=university_name
            )
            
            if created:
                print(f"✅ Universidad creada: {university_name}")

            # Crear perfil de psicólogo
            psychologist_instance = psychologist.objects.create(
                user=user,
                university=university_instance,
                description=data.get('description', '')
            )

            serializer = PsychologistSerializer(psychologist_instance)
            return Response(serializer.data, status=201)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Error al crear perfil de psicólogo: {str(e)}"}, 
                status=500
            )

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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PsychologistProfile

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


