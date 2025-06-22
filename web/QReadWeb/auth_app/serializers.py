# meu_app/serializers.py
from rest_framework import serializers
from auth_app.models import CustomUser  # Ou CustomUser, se personalizado
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    name = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')
        )
        return user
    
    def to_representation(self, instance):
        # Personaliza a resposta
        return {
            'status': 'success',
            'message': 'Usuário registrado com sucesso!',
            'success': True,
            'user': {
                'id': instance.id,
                'username': instance.username,
                'email': instance.email
            }
        }

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Usa email como identificador

    def validate(self, attrs):
        user = authenticate(
            email=attrs.get('email'),
            password=attrs.get('password')
        )
        if user is None:
            raise serializers.ValidationError('Credenciais inválidas')
        
        data = super().validate(attrs)
        data.update({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name if hasattr(user, 'name') else None,
            }
        })
        return data