from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound
from .permissions import IsFormQuestionOwnerOrReadOnly, IsOwnerOrReadOnly
from .models import (
    psychologist, 
    university, 
    forms, 
    questions, 
    answer, 
    PsychologistProfile, 
    form_response, 
    DueTests,
    PsychologistApplication
)
from .serializers import (
    PsychologistSerializer,
    PsychologistApplicationSerializer, 
    ApplicationReviewSerializer,
    UniversitySerializer, 
    FormSerializer, 
    QuestionSerializer, 
    AnswerSerializer, 
    FormResponseSerializer, 
    DueTestsSerializer,
    PsychologistProfileSerializer
)
from services.splitPDF.splitPDF import splitPDF

# Obtener modelo de usuario
User = get_user_model()


# ===== EXPORTAR TODAS LAS VISTAS =====
__all__ = [
    'AllPsychologists',
    'SpecificPsychologist',
    'current_psychologist_profile',
    'AllForms',
    'FormDetail',
    'AllQuestions',
    'QuestionDetail',
    'CreateAnswer',
    'AllFormResponse',
    'AssignDueTests',
    'SpecficDueTest',
    'AiTraining',
    'UploadProfilePic',
    'PsychologistApplicationViewSet'
]


# ===== VISTAS DE PSICÓLOGOS =====

class AllPsychologists(APIView):
    """
    Vista para listar todos los psicólogos certificados
    """
    permission_classes = []  # Permitir acceso público
    
    def get(self, request):
        """Listar todos los psicólogos con sus datos relacionados"""
        try:
            # Usar select_related para optimizar queries
            psychologists = psychologist.objects.select_related(
                'user', 
                'university'
            ).all()
            
            serializer = PsychologistSerializer(psychologists, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("❌ ERROR EN AllPsychologists:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensaje: {str(e)}")
            traceback.print_exc()
            
            return Response(
                {
                    "error": "Error al obtener psicólogos",
                    "details": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SpecificPsychologist(APIView):
    """
    Vista para obtener un psicólogo específico por ID de usuario
    """
    def get(self, request, pk=None):
        """Obtener psicólogo por user_id"""
        try:
            psychologist_obj = get_object_or_404(psychologist, user_id=pk)
            serializer = PsychologistSerializer(psychologist_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_psychologist_profile(request):
    """
    Obtener o actualizar el perfil del psicólogo autenticado
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


# ===== VISTAS DE FORMULARIOS =====

class AllForms(APIView):
    """
    Listar todos los formularios y crear nuevos
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar todos los formularios"""
        forms_qs = forms.objects.all()
        serializer = FormSerializer(forms_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Crear nuevo formulario"""
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        
        serializer = FormSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FormDetail(APIView):
    """
    Obtener, actualizar o eliminar un formulario específico
    """
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    
    def get(self, request, pk):
        """Obtener detalles del formulario"""
        try:
            form_obj = forms.objects.get(id=pk)
            serializer = FormSerializer(form_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
    
    def put(self, request, pk):
        """Actualizar formulario"""
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        
        self.check_object_permissions(request, form_obj)
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        
        serializer = FormSerializer(form_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Eliminar formulario"""
        try:
            form_obj = forms.objects.get(id=pk)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")
        
        self.check_object_permissions(request, form_obj)
        form_obj.delete()
        return Response(
            {"message": "Formulario eliminado exitosamente."}, 
            status=status.HTTP_204_NO_CONTENT
        )


# ===== VISTAS DE PREGUNTAS =====

class AllQuestions(APIView):
    """
    Listar todas las preguntas y crear nuevas
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar todas las preguntas"""
        questions_qs = questions.objects.all()
        serializer = QuestionSerializer(questions_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Crear nueva pregunta"""
        data = request.data.copy()
        data['psychologist'] = request.user.id
        
        serializer = QuestionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionDetail(APIView):
    """
    Obtener, actualizar o eliminar una pregunta específica
    """
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    
    def get(self, request, pk):
        """Obtener detalles de la pregunta"""
        try:
            question_obj = questions.objects.get(id=pk)
            serializer = QuestionSerializer(question_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
    
    def put(self, request, pk):
        """Actualizar pregunta"""
        try:
            question_obj = questions.objects.get(id=pk)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
        
        self.check_object_permissions(request, question_obj)
        data = request.data.copy()
        data['psychologist'] = request.user.id 
        
        serializer = QuestionSerializer(question_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Eliminar pregunta"""
        try:
            question_obj = questions.objects.get(id=pk)
        except questions.DoesNotExist:
            raise NotFound("Pregunta no encontrada.")
        
        self.check_object_permissions(request, question_obj)
        question_obj.delete()
        return Response(
            {"message": "Pregunta eliminada exitosamente."}, 
            status=status.HTTP_204_NO_CONTENT
        )


# ===== VISTAS DE RESPUESTAS =====

class CreateAnswer(APIView):
    """
    Crear respuestas a preguntas
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Crear nueva respuesta"""
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AllFormResponse(APIView):
    """
    Listar y crear respuestas a formularios
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar todas las respuestas"""
        responses = form_response.objects.all()
        serializer = FormResponseSerializer(responses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Crear respuesta a formulario con sus answers"""
        data = request.data
        user = request.user
        form_id = data.get("form")

        # Validar formulario
        try:
            form_obj = forms.objects.get(id=form_id)
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")

        # Crear form_response
        fr = form_response.objects.create(user=user, form=form_obj)

        # Crear answers
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

        # Calcular total
        fr.compute_total()

        serializer = FormResponseSerializer(fr, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ===== VISTAS DE TESTS ASIGNADOS =====

class AssignDueTests(APIView):
    """
    Listar y asignar tests a pacientes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar tests asignados por el psicólogo"""
        due_tests = DueTests.objects.filter(psychologist=request.user)
        serializer = DueTestsSerializer(due_tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Asignar test a paciente"""
        data = request.data
        psychologist_user = request.user

        # Validar que sea psicólogo
        if not psychologist_user.is_psychologist:
            return Response(
                {"error": "Solo los psicólogos pueden asignar tests."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Validar formulario
        try:
            form_instance = forms.objects.get(id=data['form'])
        except forms.DoesNotExist:
            raise NotFound("Formulario no encontrado.")

        # Validar paciente
        try:
            patient_instance = User.objects.get(id=data['patient'])
        except User.DoesNotExist:
            raise NotFound("Paciente no encontrado.")
        
        # Validar que no se asigne a sí mismo
        if patient_instance == psychologist_user:
            return Response(
                {"error": "No puedes asignar un test a ti mismo."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear DueTest
        due_test = DueTests.objects.create(
            psychologist=psychologist_user,
            patient=patient_instance,
            form=form_instance,
            date=data['date'],
            description=data.get('description', ""),
        )

        serializer = DueTestsSerializer(due_test)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SpecficDueTest(APIView):
    """
    Obtener, actualizar o eliminar un test específico
    """
    permission_classes = [IsFormQuestionOwnerOrReadOnly]
    
    def get(self, request, pk):
        """Obtener detalles del test"""
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        serializer = DueTestsSerializer(due_test)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Actualizar test"""
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        serializer = DueTestsSerializer(due_test, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Eliminar test"""
        try:
            due_test = DueTests.objects.get(id=pk)
        except DueTests.DoesNotExist:
            raise NotFound("DueTest no encontrado.")
        
        self.check_object_permissions(request, due_test)
        due_test.delete()
        return Response(
            {"message": "DueTest eliminado exitosamente."}, 
            status=status.HTTP_204_NO_CONTENT
        )


# ===== OTRAS VISTAS =====

class AiTraining(APIView):
    """
    Procesar PDFs para entrenamiento de IA
    """
    def post(self, request):
        """Procesar PDF"""
        data = request.data
        splitter = splitPDF()
        splitter(data["pdfFile"])
        return Response(
            {"message": "PDF procesado y datos almacenados correctamente."}, 
            status=status.HTTP_200_OK
        )


class UploadProfilePic(APIView):
    """
    Subir foto de perfil de psicólogo
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Procesar y guardar imagen de perfil"""
        user = request.user
        uploaded_file = request.FILES.get('profile_pic')

        if not uploaded_file:
            return Response(
                {"error": "No se proporcionó ninguna imagen."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener o crear perfil
        profile, created = PsychologistProfile.objects.get_or_create(user=user)

        # Procesar y guardar imagen
        profile.save_profile_pic(uploaded_file)

        return Response(
            {"message": "Imagen de perfil subida y procesada correctamente."}, 
            status=status.HTTP_200_OK
        )


# ===== VIEWSET DE APLICACIONES =====

class PsychologistApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar solicitudes de conversión a psicólogo
    """
    serializer_class = PsychologistApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar queryset según el usuario"""
        user = self.request.user
        
        if user.is_superuser:
            return PsychologistApplication.objects.all()
        
        return PsychologistApplication.objects.filter(user=user)
    
    def get_permissions(self):
        """Permisos especiales para ciertas acciones"""
        if self.action in ['review', 'pending']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """Crear nueva solicitud"""
        if request.user.is_psychologist:
            return Response(
                {'error': 'Ya eres un psicólogo certificado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        """Obtener solicitud del usuario actual"""
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
        """Listar solicitudes pendientes (solo admins)"""
        applications = PsychologistApplication.objects.filter(status='pending')
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review(self, request, pk=None):
        """Aprobar o rechazar solicitud (solo admins)"""
        application = self.get_object()
        
        if application.status != 'pending':
            return Response(
                {'error': 'Esta solicitud ya fue revisada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review_serializer = ApplicationReviewSerializer(data=request.data)
        review_serializer.is_valid(raise_exception=True)
        
        action_type = review_serializer.validated_data['action']
        
        if action_type == 'approve':
            # Aprobar
            application.status = 'approved'
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            # Convertir en psicólogo
            user = application.user
            user.is_psychologist = True
            user.save()
            
            # Crear perfil
            psychologist.objects.get_or_create(
                user=user,
                defaults={'description': application.professional_description}
            )
            
            return Response({
                'message': f'Solicitud aprobada. {user.username} ahora es psicólogo',
                'data': self.get_serializer(application).data
            })
        
        else:  # reject
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
        """Cancelar solicitud propia"""
        application = self.get_object()
        
        if application.user != request.user:
            return Response(
                {'error': 'No puedes cancelar esta solicitud'},
                status=status.HTTP_403_FORBIDDEN
            )
        
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