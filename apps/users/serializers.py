# apps/users/serializers.py
from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'SleepState', 'is_psychologist', 'description', 'profile_pic', 'password']
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'},
        }

    def get_profile_pic(self, obj):
        """
        Devuelve la URL completa de la imagen de perfil
        """
        if obj.profile_pic:
            request = self.context.get('request')
            if request:
                # Usar request.build_absolute_uri() para construir la URL completa
                return request.build_absolute_uri(obj.profile_pic.url)
            else:
                # Fallback si no hay request en el contexto
                return obj.profile_pic.url
        return None

    def validate_password(self, value):
        # Si el regex NO coincide, lanza ValidationError
        if not re.search(
            r'^(?=(.*[A-Z]){1,})(?=(.*\d){1,})(?=(.*[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>\/?]){1,}).{12,}$',
            value
        ):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 12 caracteres, 1 mayúscula, 1 número  y un carácter especial."
            )
        return value  # Si pasa la validación, devuelve el valor

    def create(self, validated_data):
        # Extraer profile_pic si está presente (ya que ahora es SerializerMethodField en read)
        profile_pic = self.initial_data.get('profile_pic')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            description=validated_data.get('description', ''),
        )
        
        # Asignar profile_pic si se proporcionó
        if profile_pic:
            user.profile_pic = profile_pic
            
        user.set_password(validated_data['password'])  # La validación ya ocurrió en validate_password
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Actualizar una instancia de usuario existente
        """
        # Extraer la contraseña si está presente
        password = validated_data.pop('password', None)
        
        # Actualizar los campos restantes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar la contraseña si se proporcionó
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance