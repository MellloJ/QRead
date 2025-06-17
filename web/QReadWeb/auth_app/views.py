from django.shortcuts import render
from django.views import View
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from auth_app.models import CustomUser 

# Create your views here.
class Login(View):
    def get(self, request):
        return render(request, 'auth_app/login.html')
    
class Register(View):
    def get(self, request):
        return render(request, 'auth_app/register.html')
    
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # Qualquer um pode registrar

    response = {
        "status": "success",
        "message": "Usuário registrado com sucesso.",
        "success": True,
    }