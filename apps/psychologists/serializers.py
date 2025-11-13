from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from .models import (
    psychologist as PsychologistModel,
    university as UniversityModel,
    forms as FormModel,
    questions as QuestionModel,
    answer as AnswerModel,
    PsychologistProfile as PsychologistProfileModel,
    form_response as FormResponseModel,
    DueTests as DueTestsModel,
    PsychologistApplication
)

# Obtener el modelo de usuario personalizado
User = get_user_model()

# ===== SERIALIZADORES BASE =====

class UniversitySerializer(serializers.ModelSerializer):
    """Serializador para universidades"""
    class Meta:
        model = UniversityModel
        fields = ['id', 'name']


class SimpleUserSerializer(serializers.ModelSerializer):
    """Serializador simple para Usuario (para evitar duplicación)"""
    profile_pic = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic']
    
    def get_profile_pic(self, obj):
        """Obtener foto de perfil desde profile_pic_base64"""
        if hasattr(obj, 'profile_pic_base64') and obj.profile_pic_base64:
            return obj.profile_pic_base64
        
        # Intentar desde PsychologistProfile si existe
        try:
            profile = PsychologistProfileModel.objects.get(user=obj)
            return profile.profile_pic_base64
        except PsychologistProfileModel.DoesNotExist:
            return None


# ===== SERIALIZADORES DE PSICÓLOGOS =====

class PsychologistSerializer(serializers.ModelSerializer):
    """Serializador completo para Psicólogos"""
    user = SimpleUserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    profile_pic = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = PsychologistModel
        fields = ['user', 'username', 'university', 'description', 'startDate', 'profile_pic']
    
    def get_profile_pic(self, obj):
        """Obtener foto de perfil del psicólogo"""
        # Primero del User
        if hasattr(obj.user, 'profile_pic_base64') and obj.user.profile_pic_base64:
            return obj.user.profile_pic_base64
        
        # Luego del PsychologistProfile
        try:
            profile = PsychologistProfileModel.objects.get(user=obj.user)
            return profile.profile_pic_base64
        except PsychologistProfileModel.DoesNotExist:
            return None
    
    def get_username(self, obj):
        """Obtener username del usuario asociado"""
        return obj.user.username if obj.user else None


# ===== SERIALIZADORES DE FORMULARIOS Y PREGUNTAS =====

class QuestionSerializer(serializers.ModelSerializer):
    """Serializador para Preguntas"""
    class Meta:
        model = QuestionModel
        fields = [
            'id',
            'psychologist',
            'question_text',
            'min_value',
            'max_value'
        ]


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    psychologist = SimpleUserSerializer(read_only=True)
    questions_ids = serializers.PrimaryKeyRelatedField(
        queryset=QuestionModel.objects.all(),
        many=True,
        write_only=True,
        source='questions',
        pk_field=serializers.UUIDField(format='hex')
    )

    class Meta:
        model = FormModel
        fields = [
            'id',
            'psychologist',
            'title',
            'description',
            'questions',
            'questions_ids'
        ]

    def create(self, validated_data):
        # Extraer preguntas
        questions_data = validated_data.pop('questions', [])
        # Asignar psicólogo desde el request
        user = self.context['request'].user
        form_obj = FormModel.objects.create(psychologist=user, **validated_data)
        form_obj.questions.set(questions_data)
        return form_obj

    def update(self, instance, validated_data):
        # Actualizar campos del formulario
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Actualizar preguntas si se envían
        if questions_data is not None:
            instance.questions.set(questions_data)
        return instance


# ===== SERIALIZADORES DE RESPUESTAS =====

class AnswerSerializer(serializers.ModelSerializer):
    """Serializador para Respuestas a Preguntas"""
    class Meta:
        model = AnswerModel
        fields = [
            'id',
            'response',
            'question',
            'value'
        ]

    def validate_value(self, value):
        """Validar que el valor esté en el rango correcto"""
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                "El valor debe estar entre 1 y 10 en la escala numérica."
            )
        return value


class FormResponseSerializer(serializers.ModelSerializer):
    """Serializador para Respuestas de Formularios"""
    form = FormSerializer(read_only=True)
    user = SimpleUserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = FormResponseModel
        fields = [
            'id', 
            'form',
            'user',
            'created_at',
            'total_score',
            'answers'
        ]


# ===== SERIALIZADORES DE TESTS ASIGNADOS =====

class DueTestsSerializer(serializers.ModelSerializer):
    """Serializador para Tests Asignados"""
    patient = SimpleUserSerializer(read_only=True)
    psychologist = SimpleUserSerializer(read_only=True)
    form = FormSerializer(read_only=True)
    
    class Meta:
        model = DueTestsModel
        fields = [
            'id',
            'psychologist',
            'patient',
            'form',
            'date',
            'description',
            'is_completed',
            'access_code'
        ]
    
    def validate_date(self, value):
        """Validar que la fecha sea futura"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "La fecha debe ser futura."
            )
        return value
    
    def create(self, validated_data):
        """Crear test con is_completed en False"""
        validated_data['is_completed'] = False
        return super().create(validated_data)


# ===== SERIALIZADORES DE PERFIL =====

class PsychologistProfileSerializer(serializers.ModelSerializer):
    """Serializador para Perfil de Psicólogo (fotos)"""
    class Meta:
        model = PsychologistProfileModel
        fields = ['user', 'profile_pic_base64']

    def update(self, instance, validated_data):
        """Actualizar perfil con imagen procesada"""
        from services.imageHandler.imageHandler import ImageHandler
        
        uploaded_file = self.context['request'].FILES.get('profile_pic')
        if uploaded_file:
            handler = ImageHandler(base_dir='psychologists')
            instance.profile_pic_base64 = handler.process_image(instance, uploaded_file)
        return super().update(instance, validated_data)


# ===== SERIALIZADORES DE APLICACIONES =====

class PsychologistApplicationSerializer(serializers.ModelSerializer):
    """Serializador para Solicitudes de Conversión a Psicólogo"""
    user = SimpleUserSerializer(read_only=True)
    
    class Meta:
        model = PsychologistApplication
        fields = [
            'id',
            'user',
            'university_name',
            'professional_description',
            'credentials_document',
            'status',
            'created_at',
            'updated_at',
            'reviewed_by',
            'reviewed_at',
            'rejection_reason'
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'created_at',
            'updated_at',
            'reviewed_by',
            'reviewed_at'
        ]
    
    def validate(self, data):
        """Validar que el usuario pueda crear una solicitud"""
        user = self.context['request'].user
        
        # Verificar solicitud pendiente
        if PsychologistApplication.objects.filter(
            user=user,
            status='pending'
        ).exists():
            raise serializers.ValidationError(
                "Ya tienes una solicitud pendiente"
            )
        
        # Verificar si ya es psicólogo
        if user.is_psychologist:
            raise serializers.ValidationError(
                "Ya eres un psicólogo certificado"
            )
        
        return data


class ApplicationReviewSerializer(serializers.Serializer):
    """Serializador para Aprobar/Rechazar Solicitudes"""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )
    
    def validate(self, data):
        """Validar que se proporcione razón al rechazar"""
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError(
                "Debes proporcionar una razón para rechazar la solicitud"
            )
        return data