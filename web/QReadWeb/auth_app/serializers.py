# meu_app/serializers.py
from rest_framework import serializers
from auth_app.models import CustomUser  # Ou CustomUser, se personalizado
from rest_framework.validators import UniqueValidator

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


    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
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