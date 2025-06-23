from django.contrib import admin
from django.urls import path, include
from core.views import *
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter

app_name = 'core'

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')
router.register(r'scans', ScanViewSet, basename='scan')

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    path('perfil/', Perfil.as_view(), name='perfil'),
    path('configuracoes/', Configuracoes.as_view(), name='configuracoes'),
    path('sair/', LogoutView.as_view(), name='sair'),
    path('qr/create/', CreateQRCode.as_view(), name='create_qr_code'),
    path('qr/<str:short_url>/', QRRedirect.as_view(), name='qr_redirect'),
    path('api/', include(router.urls)),
    path('api/scan-stats/<str:short_url>/', scan_stats, name='scan_stats_specific'),
    path('api/scan-stats/', scan_stats, name='scan_stats'),
    path('qr/details/<str:short_url>/', QRCodeDetails.as_view(), name='qr_code_details'), 
]
