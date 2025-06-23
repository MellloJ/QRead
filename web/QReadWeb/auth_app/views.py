from django.shortcuts import render
from django.views import View
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from auth_app.models import CustomUser 
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginWeb(View):
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'message': 'Login realizado com sucesso.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Usuário ou senha inválidos.'}, status=401)