from django.contrib import admin
from django.urls import path
from auth_app.views import *

urlpatterns = [
    path('', Login.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
]
