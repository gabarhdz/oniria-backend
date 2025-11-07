# apps/users/serializers.py
from rest_framework import serializers
from .models import User
import re


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_pic = serializers.ImageField(write_only=True, required=False, allow_null=True)
    profile_pic_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'url', 
            'id', 
            'username', 
            'email',
            'is_psychologist', 
            'description', 
            'profile_pic',  # Para escritura (archivo)
            'profile_pic_url',  # Para lectura (base64)
            'password',
            'date_joined'
        ]
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'},
        }

    def get_profile_pic_url(self, obj):
        """
        Devuelve la imagen en base64 con el prefijo data:image
        """
        if obj.profile_pic_base64:
            # Si ya tiene el prefijo data:image, devolverlo tal cual
            if obj.profile_pic_base64.startswith('data:image'):
                return obj.profile_pic_base64
            # Si no, agregar el prefijo (asumiendo JPEG por defecto)
            return f"data:image/jpeg;base64,{obj.profile_pic_base64}"
        return None

    def validate_password(self, value):
        """Validar fortaleza de la contraseña"""
        if not re.search(
            r'^(?=(.*[A-Z]){1,})(?=(.*\d){1,})(?=(.*[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>\/?]){1,}).{12,}$',
            value
        ):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 12 caracteres, 1 mayúscula, 1 número y un carácter especial."
            )
        return value

    def create(self, validated_data):
        """
        Crear usuario con imagen en base64
        """
        # Extraer campos especiales
        password = validated_data.pop('password', None)
        profile_pic_file = validated_data.pop('profile_pic', None)
        
        # Crear usuario
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            description=validated_data.get('description', ''),
            is_psychologist=validated_data.get('is_psychologist', False)
        )
        
        # Establecer contraseña
        if password:
            user.set_password(password)
        
        # Procesar imagen si existe
        if profile_pic_file:
            try:
                user.save_profile_pic(profile_pic_file)
            except Exception as e:
                # Si falla el procesamiento de imagen, eliminar usuario creado
                user.delete()
                raise serializers.ValidationError({
                    'profile_pic': f'Error al procesar la imagen: {str(e)}'
                })
        
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Actualizar usuario con imagen en base64
        """
        # Extraer campos especiales
        password = validated_data.pop('password', None)
        profile_pic_file = validated_data.pop('profile_pic', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporcionó
        if password:
            instance.set_password(password)
        
        # Procesar imagen si se proporcionó
        if profile_pic_file:
            try:
                instance.save_profile_pic(profile_pic_file)
            except Exception as e:
                raise serializers.ValidationError({
                    'profile_pic': f'Error al procesar la imagen: {str(e)}'
                })
        
        instance.save()
        return instance