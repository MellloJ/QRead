from django.contrib import admin
from django.urls import path, include
from core.views import *

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
]
