from rest_framework import serializers
from .models import User
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'SleepState', 'is_psychologist', 'description', 'profile_pic', 'password']
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'},
        }

    def validate_password(self, value):
        # Si el regex NO coincide, lanza ValidationError
        if not re.search(
            r'^(?=(.*[A-Z]){1,})(?=(.*\d){1,})(?=(.*[!@#$%^&*()_+\-=\[\]{}|;:\'",.<>\/?]){1,}).{12,}$',
            value
        ):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 12 caracteres, 1 mayúscula, 3 números y un carácter especial."
            )
        return value  # Si pasa la validación, devuelve el valor

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            description=validated_data['description'],
            profile_pic=validated_data['profile_pic']
        )
        user.set_password(validated_data['password'])  # La validación ya ocurrió en validate_password
        user.save()
        return user
    

