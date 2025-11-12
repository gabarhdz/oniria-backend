# serializers.py generado automáticamente
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
    DueTests as DueTestsModel
)
from services.imageHandler.imageHandler import ImageHandler

# Obtener el modelo de usuario personalizado
User = get_user_model()

# Serializador para el modelo de usuario
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic_base64']

# Serializador para el modelo de universidad
class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UniversityModel
        fields = ['id', 'name']

# Serializador para el modelo de psicólogo
class PsychologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    
    class Meta:
        model = PsychologistModel
        fields = ['user', 'university', 'description', 'startDate']

# Serializador para el modelo de preguntas
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = [
            'id',
            'psychologist',
            'question_text',
            'min_value',
            'max_value'
        ]

# Serializador para el modelo de formularios
class FormSerializer(serializers.ModelSerializer):
    # Mostrar las preguntas asociadas al formulario
    questions = QuestionSerializer(many=True, read_only=True)
    psychologist = UserSerializer(read_only=True)
    # Permitir asociar preguntas al formulario mediante sus UUIDs
    questions_ids = serializers.PrimaryKeyRelatedField(
        queryset=QuestionModel.objects.all(), many=True, write_only=True, source='questions', pk_field=serializers.UUIDField(format='hex')
    )
    
    class Meta:
        model = FormModel
        fields = [
            'id',
            'psychologist',
            'title',
            'description',
            'questions',  # Preguntas asociadas (lectura)
            'questions_ids'  # UUIDs de preguntas asociadas (escritura)
        ]
    
    def create(self, validated_data):
        """
        Crear un formulario con preguntas asociadas.
        """
        # Extraer las preguntas asociadas
        questions_data = validated_data.pop('questions', [])
        form_obj = FormModel.objects.create(**validated_data)
        # Asociar las preguntas al formulario
        form_obj.questions.set(questions_data)
        return form_obj
    
    def update(self, instance, validated_data):
        """
        Actualizar un formulario y sus preguntas asociadas.
        """
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            instance.questions.set(questions_data)  # Actualizar preguntas asociadas
        return instance

# Serializador para el modelo de respuestas
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            'id',
            'response',
            'question',
            'value',
            'note'
        ]
    
    def validate_value(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                "El valor debe estar entre 1 y 10 en la escala numérica."
            )
        return value

# Serializador para el modelo de perfil de psicólogo
class PsychologistProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychologistProfileModel
        fields = ['user', 'profile_pic_base64']

    def update(self, instance, validated_data):
        uploaded_file = self.context['request'].FILES.get('profile_pic')
        if uploaded_file:
            handler = ImageHandler(base_dir='psychologists')
            instance.profile_pic_base64 = handler.process_image(instance, uploaded_file)
        return super().update(instance, validated_data)
    
class FormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponseModel
        fields = ['id', 
                'form',
                'user',
                'created_at',
                'total_score']
    


class DueTestsSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    psychologist = UserSerializer(read_only=True)
    form = FormSerializer(read_only=True)
    class Meta:
        model = DueTestsModel
        fields = ['id',
                  'psychologist',
                  'patient',
                  'form',
                  'date',
                  'description',
                  'is_completed',
                  'access_code']
    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Fecha incorrecta, debe ser una fecha futura.")
        return value
    def create(self, validated_data):
        validated_data['is_completed'] = False
        return super().create(validated_data)
    

