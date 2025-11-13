from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .permissions import IsFormQuestionOwnerOrReadOnly, IsOwnerOrReadOnly
from .models import psychologist, university, forms, questions, answer, PsychologistProfile, form_response, DueTests    
from .serializers import PsychologistSerializer,PsychologistApplicationSerializer, ApplicationReviewSerializer, PsychologistApplication, UniversitySerializer, FormSerializer, QuestionSerializer, AnswerSerializer, FormResponseSerializer, DueTestsSerializer
from services.splitPDF.splitPDF import splitPDF


# Create your views here.

class AllPsychologists(APIView):
    def get(self, request):
        try:
            psychologists = psychologist.objects.select_related('user', 'university').all()
            serializer = PsychologistSerializer(psychologists, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            import traceback
            print("ERROR EN AllPsychologists:", e)
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

        try:
            # Verificar que el usuario sea psicólogo
            if not user.is_psychologist:
                return Response(
                    {"error": "El usuario debe estar marcado como psicólogo"}, 
                    status=400
                )
            
            # Verificar que no exista ya un perfil de psicólogo
            if psychologist.objects.filter(user=user).exists():
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
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_psychologist_profile(request):
    """
    Obtener o actualizar el perfil del psicólogo actual
    """
    try:
        psychologist_profile = psychologist.objects.get(user=request.user)
    except psychologist.DoesNotExist:
        return Response(
            {'error': 'No tienes un perfil de psicólogo'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = PsychologistSerializer(psychologist_profile)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = PsychologistSerializer(
            psychologist_profile, 
            data=request.data, 
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpecificPsychologist(APIView):
    def get(self, _request, pk=None):
        psychologist_obj = get_object_or_404(psychologist, user_id=pk)
        serializer = PsychologistSerializer(psychologist_obj)
        return Response(serializer.data)
    
class AiTraining(APIView):
    def post(self, request):
        data = request.data
        splitter = splitPDF()
        splitter(data["pdfFile"])
        return Response({"message": "PDF procesado y datos almacenados correctamente."}, status=200)
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

class SpecficDueTest(APIView):
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    
    def get(self, request, pk, *args, **kwargs):
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        serializer = DueTestsSerializer(due_test)
        return Response(serializer.data)
    def put(self, request, pk, *args, **kwargs):
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        data = request.data
        serializer = DueTestsSerializer(due_test, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    def delete(self, request, pk, *args, **kwargs):
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        due_test.delete()
        return Response({"message": "DueTest eliminado exitosamente."}, status=204)


class PsychologistApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar solicitudes de conversión a psicólogo
    """
    serializer_class = PsychologistApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Superusers pueden ver todas las solicitudes
        if user.is_superuser:
            return PsychologistApplication.objects.all()
        
        # Usuarios normales solo ven sus propias solicitudes
        return PsychologistApplication.objects.filter(user=user)
    
    def get_permissions(self):
        # Solo superusers pueden aprobar/rechazar
        if self.action in ['review', 'list_pending']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Crear nueva solicitud de conversión a psicólogo
        """
        # Verificar que el usuario no sea ya psicólogo
        if request.user.is_psychologist:
            return Response(
                {'error': 'Ya eres un psicólogo certificado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que no tenga solicitud pendiente
        if PsychologistApplication.objects.filter(
            user=request.user,
            status='pending'
        ).exists():
            return Response(
                {'error': 'Ya tienes una solicitud pendiente'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        return Response(
            {
                'message': 'Solicitud enviada exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def my_application(self, request):
        """
        Obtener la solicitud actual del usuario
        """
        application = PsychologistApplication.objects.filter(
            user=request.user
        ).order_by('-created_at').first()
        
        if not application:
            return Response(
                {'message': 'No tienes solicitudes'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """
        Listar todas las solicitudes pendientes (solo superusers)
        """
        applications = PsychologistApplication.objects.filter(
            status='pending'
        )
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review(self, request, pk=None):
        """
        Aprobar o rechazar una solicitud (solo superusers)
        """
        application = self.get_object()
        
        # Validar que la solicitud esté pendiente
        if application.status != 'pending':
            return Response(
                {'error': 'Esta solicitud ya fue revisada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de revisión
        review_serializer = ApplicationReviewSerializer(data=request.data)
        review_serializer.is_valid(raise_exception=True)
        
        action_type = review_serializer.validated_data['action']
        
        if action_type == 'approve':
            # Aprobar solicitud
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            # Convertir usuario en psicólogo
            user = application.user
            user.is_psychologist = True
            user.save()
            
            # Crear perfil de psicólogo
            psychologist.objects.get_or_create(
                user=user,
                defaults={
                    'description': application.professional_description
                }
            )
            
            return Response({
                'message': f'Solicitud aprobada. {user.username} ahora es psicólogo',
                'data': self.get_serializer(application).data
            })
        
        elif action_type == 'reject':
            # Rechazar solicitud
            application.status = 'rejected'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.rejection_reason = review_serializer.validated_data.get(
                'rejection_reason', ''
            )
            application.save()
            
            return Response({
                'message': 'Solicitud rechazada',
                'data': self.get_serializer(application).data
            })
    
    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        """
        Cancelar solicitud propia (solo si está pendiente)
        """
        application = self.get_object()
        
        # Verificar que la solicitud pertenezca al usuario
        if application.user != request.user:
            return Response(
                {'error': 'No puedes cancelar esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que esté pendiente
        if application.status != 'pending':
            return Response(
                {'error': 'Solo puedes cancelar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.delete()
        
        return Response(
            {'message': 'Solicitud cancelada exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )
