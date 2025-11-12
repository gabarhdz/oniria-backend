from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from .permissions import IsFormQuestionOwnerOrReadOnly, IsOwnerOrReadOnly
from .models import psychologist, university, forms, questions, answer, PsychologistProfile, form_response, DueTests    
from .serializers import PsychologistSerializer, UniversitySerializer, FormSerializer, QuestionSerializer, AnswerSerializer, FormResponseSerializer, DueTestsSerializer
from services.splitPDF.splitPDF import splitPDF
from django.conf import settings
from django.contrib.auth import get_user_model

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
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        
        serializer = FormSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class FormDetail(APIView):
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    """
    Permite recuperar los detalles de un formulario específico.
    """
    def get(self, request, pk, *args, **kwargs):
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        serializer = FormSerializer(form_obj)
        return Response(serializer.data)
    def delete(self, request, pk, *args, **kwargs):
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        self.check_object_permissions(request,form_obj)
        form_obj.delete()
        return Response({"message": "Formulario eliminado exitosamente."}, status=204)
    def put(self, request, pk, *args, **kwargs):
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        self.check_object_permissions(request,form_obj)
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        serializer = FormSerializer(form_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

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
        data = request.data.copy()
        data['psychologist'] = request.user.id
        serializer = QuestionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

class QuestionDetail(APIView):
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    def get(self, request, pk, *args, **kwargs):
        try:
            question_obj = questions.objects.get(id=pk)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
        serializer = QuestionSerializer(question_obj)
        return Response(serializer.data)
    def delete(self, request, pk, *args, **kwargs):
        try:
            question_obj = questions.objects.get(id=pk)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
        self.check_object_permissions(request,question_obj)
        question_obj.delete()
        return Response({"message": "Pregunta eliminada exitosamente."}, status=204)
    def put(self, request, pk, *args, **kwargs):
        try:
            question_obj = questions.objects.get(id=pk)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
        self.check_object_permissions(request,question_obj)
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        serializer = QuestionSerializer(question_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

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


class AllFormResponse(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """
        Listar todas las respuestas al formulario.
        Usar many=True al serializar queryset para evitar AttributeError.
        """
        responses = form_response.objects.all()
        serializer = FormResponseSerializer(responses, many=True, context={'request': request})
        return Response(serializer.data, status=200)
    
    def post(self, request, *args, **kwargs):
        """
        Crear una respuesta de formulario. Espera:
        {
          "form": "<form_uuid>",
          "answers": [{"question": "<q_uuid>", "value": 5}, ...]  # opcional
        }
        """
        data = request.data
        user = request.user
        form_id = data.get("form")

        # validar form
        try:
            form_obj = forms.objects.get(id=form_id)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")

        # crear form_response
        fr = form_response.objects.create(user=user, form=form_obj)

        # crear answers si vienen en la petición
        answers_payload = data.get("answers", [])
        for a in answers_payload:
            qid = a.get("question")
            value = a.get("value")
            if qid is None or value is None:
                continue
            try:
                q = questions.objects.get(id=qid)
            except questions.DoesNotExist:
                continue
            answer.objects.create(response=fr, question=q, value=value)

        # calcular y almacenar total
        fr.compute_total()

        serializer = FormResponseSerializer(fr, context={'request': request})
        return Response(serializer.data, status=201)

class AssignDueTests(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Listar todos los tests asignados por el psicólogo autenticado.
        """
        due_tests = DueTests.objects.filter(psychologist=request.user)
        serializer = DueTestsSerializer(due_tests, many=True)
        return Response(serializer.data, status=200)
    def post(self, request, *args, **kwargs):
        """
        Asignar un test a un paciente.forms pf 
        """
        data = request.data
        psychologist = request.user

        # Obtener el modelo de usuario real
        User = get_user_model()

        # Validar que el formulario existe
        try:
            form_instance = forms.objects.get(id=data['form'])
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")

        # Validar que el paciente existe
        try:
            patient_instance = User.objects.get(id=data['patient'])
        except User.DoesNotExist:
            raise NotFound("Paciente no encontrado.")
        
        if patient_instance == psychologist:
            return Response({"error": "No puedes asignar un test a ti mismo."}, status=400)
        
        if psychologist.is_psychologist is False:
            return Response({"error": "Solo los psicólogos pueden asignar tests."}, status=403)

        # Crear el DueTest
        due_test = DueTests.objects.create(
            psychologist=psychologist,
            patient=patient_instance,
            form=form_instance,
            date=data['date'],
            description=data.get('description', ""),
        )

        # Serializar y devolver la respuesta
        serializer = DueTestsSerializer(due_test)
        return Response(serializer.data, status=201)

    def get(self, request, *args, **kwargs):
        """
        Listar todos los tests asignados por el psicólogo autenticado.
        """
        due_tests = DueTests.objects.filter(psychologist=request.user)
        serializer = DueTestsSerializer(due_tests, many=True)
        return Response(serializer.data, status=200)