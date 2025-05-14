# serializers.py generado autom�ticamente

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['url','id','username','email','first_name','last_name','SleepState','is_psychologist','description','profile_pic','password']
        extra_kwargs = {
            'url': {'view_name': 'user-detail', 'lookup_field': 'pk'},
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            description=validated_data['description'],
            profile_pic=validated_data['profile_pic']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

