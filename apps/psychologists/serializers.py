# serializers.py generado autom�ticamente
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import psychologist, university, forms, questions as QuestionModel, answer, PsychologistProfile
from services.imageHandler.imageHandler import ImageHandler

User = get_user_model()

# ...existing code...
class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic']

    def get_profile_pic(self, obj):
        # Intentar obtener profile_pic directamente en el modelo User
        pic = getattr(obj, 'profile_pic', None)
        if pic:
            try:
                return pic.url
            except Exception:
                return pic
        # Intentar posibles relaciones habituales (profile, psychologistprofile, userprofile)
        for rel in ('profile', 'psychologistprofile', 'userprofile'):
            related = getattr(obj, rel, None)
            if related:
                pic = getattr(related, 'profile_pic', None)
                if pic:
                    try:
                        return pic.url
                    except Exception:
                        return pic
        return None
# ...existing code...

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = university
        fields = ['id', 'name']

class PsychologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    
    class Meta:
        model = psychologist
        fields = ['user', 'university', 'description', 'startDate']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = [
            'id',
            'psychologist',
            'question_text',  # Faltaba una coma aquí
            'min_value',
            'max_value'
        ]
        


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    questions_ids = serializers.PrimaryKeyRelatedField(
        queryset=QuestionModel.objects.all(), many=True, write_only=True, source='questions'
    )
    
    class Meta:
        model = forms
        fields = [
            'id',
            'psychologist',
            'title',
            'description',
            'questions',
            'questions_ids'
        ]
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        form_obj = forms.objects.create(**validated_data)
        form_obj.questions.set(questions_data)
        return form_obj
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            instance.questions.set(questions_data)
        return instance

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = answer
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
                
            )
        return value

class PsychologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    university = UniversitySerializer(read_only=True)
    university_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = psychologist
        fields = ['user', 'university', 'university_name', 'description', 'startDate']
    
    def create(self, validated_data):
        university_name = validated_data.pop('university_name', None)
        
        if university_name:
            university_instance, _ = university.objects.get_or_create(
                name=university_name
            )
            validated_data['university'] = university_instance
        
        return super().create(validated_data)