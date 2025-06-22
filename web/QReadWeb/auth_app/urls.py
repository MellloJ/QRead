from django.contrib import admin
from django.urls import path
from auth_app.views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('login/register/', Register.as_view(), name='register'),
    path('login/api/register/', RegisterView.as_view(), name='registerAPI'),
    path('login/api/login/', CustomTokenObtainPairView.as_view(), name='loginAPI'),
]
