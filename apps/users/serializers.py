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
            'profile_pic',  # Para escritura
            'profile_pic_url',  # Para lectura
            'password',
            'date_joined'
        ]
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'},
        }

    def get_profile_pic_url(self, obj):
        """
        Devuelve la imagen base64 con prefijo data:image
        """
        if not obj.profile_pic_base64:
            return None
            
        # Si ya tiene el prefijo, devolverlo tal cual
        if obj.profile_pic_base64.startswith('data:image'):
            return obj.profile_pic_base64
        
        # Si no tiene prefijo, agregarlo (para datos legacy)
        return f"data:image/jpeg;base64,{obj.profile_pic_base64}"

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
            user.save()
        
        # Procesar imagen si existe
        if profile_pic_file:
            try:
                user.save_profile_pic(profile_pic_file)
                print(f"✅ Imagen guardada para usuario {user.username}")
                print(f"📷 Base64 guardado (primeros 100 chars): {user.profile_pic_base64[:100] if user.profile_pic_base64 else 'None'}")
            except Exception as e:
                print(f"❌ Error al procesar imagen: {str(e)}")
                user.delete()
                raise serializers.ValidationError({
                    'profile_pic': f'Error al procesar la imagen: {str(e)}'
                })
        
        return user

    def update(self, instance, validated_data):
        """
        Actualizar usuario con imagen en base64
        """
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
                print(f"✅ Imagen actualizada para usuario {instance.username}")
                print(f"📷 Base64 actualizado (primeros 100 chars): {instance.profile_pic_base64[:100] if instance.profile_pic_base64 else 'None'}")
            except Exception as e:
                print(f"❌ Error al procesar imagen: {str(e)}")
                raise serializers.ValidationError({
                    'profile_pic': f'Error al procesar la imagen: {str(e)}'
                })
        
        instance.save()
        return instance