from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('login/', include('auth_app.urls')),
    path('user/', include('users.urls')),
]
