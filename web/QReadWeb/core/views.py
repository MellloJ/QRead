from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from .models import QRCode, Scan
import geoip2.database
from django.conf import settings
from django.urls import reverse
import json
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import QRCodeSerializer, ScanSerializer
from rest_framework import status


# Create your views here.
class Index(View):
    def get(self, request):
        return render(request, 'core/index.html')
    
class Dashboard(View, LoginRequiredMixin):
    def get(self, request):
        qrcodes = QRCode.objects.filter(user=request.user)
        scans = Scan.objects.filter(qr_code__user=request.user)
        
        # Dados para gráficos
        last_7_days = [timezone.now().date() - timedelta(days=x) for x in range(6, -1, -1)]
        scan_counts = (
            scans.filter(scan_time__date__in=last_7_days)
            .values('scan_time__date')
            .annotate(count=Count('id'))
            .order_by('scan_time__date')
        )
        scan_data = {str(day): 0 for day in last_7_days}
        for entry in scan_counts:
            scan_data[str(entry['scan_time__date'])] = entry['count']
        
        locations = (
            scans.values('city', 'country')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        context = {
            'qrcodes': qrcodes,
            'scans': scans,
            'scan_data': json.dumps(scan_data),
            'locations': locations,
        }
        return render(request, 'core/dashboard.html', context)
    
class Perfil(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, 'core/perfil.html')  
    
class Configuracoes(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, 'core/configuracoes.html')
    
class CreateQRCode(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, 'core/create_qr_code.html')

    def post(self, request):
        content = request.POST.get('content')
        if content:
            qr_code = QRCode.objects.create(user=request.user, content=content)
            return HttpResponseRedirect(reverse('core:dashboard'))
        return render(request, 'core/create_qr_code.html', {'error': 'Content is required.'})
    
class QRRedirect(View):
    def get(self, request, short_url):
        try:
            qr_code = get_object_or_404(QRCode, short_url=short_url)
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')  # Fallback para IP inválido
            
            # Registrar escaneamento
            reader = geoip2.database.Reader(settings.GEOIP_PATH)
            city = country = 'Desconhecido'
            try:
                response = reader.city(ip)
                city = response.city.name or 'Desconhecido'
                country = response.country.name or 'Desconhecido'
            except geoip2.errors.AddressNotFoundError:
                # IP não encontrado (ex.: 127.0.0.1)
                pass
            except Exception as e:
                # Outros erros (ex.: banco de dados corrompido)
                pass
            finally:
                reader.close()
            
            Scan.objects.create(
                qr_code=qr_code,
                ip_address=ip,
                city=city,
                country=country
            )
            
            return HttpResponseRedirect(qr_code.content)
        except QRCode.DoesNotExist:
            return render(request, 'core/404.html', status=404)
        
class QRCodeDetails(View, LoginRequiredMixin):
    def get(self, request, short_url):
        qr_code = get_object_or_404(QRCode, short_url=short_url, user=request.user)
        scans = qr_code.scans.all()
        
        last_7_days = [timezone.now().date() - timedelta(days=x) for x in range(6, -1, -1)]
        scan_counts = (
            scans.filter(scan_time__date__in=last_7_days)
            .values('scan_time__date')
            .annotate(count=Count('id'))
            .order_by('scan_time__date')
        )
        scan_data = {str(day): 0 for day in last_7_days}
        for entry in scan_counts:
            scan_data[str(entry['scan_time__date'])] = entry['count']
        
        locations = (
            scans.values('city', 'country')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        context = {
            'qr_code': qr_code,
            'scans': scans,
            'scan_data': json.dumps(scan_data),
            'locations': locations,
        }
        return render(request, 'core/qr_code_details.html', context)
        
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('dashboard'))
    
# Views da API
class QRCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QRCode.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ScanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ScanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Scan.objects.filter(qr_code__user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def scan_stats(request, short_url=None):
    if short_url:
        qr_code = get_object_or_404(QRCode, short_url=short_url, user=request.user)
        scans = qr_code.scans.all()
    else:
        scans = Scan.objects.filter(qr_code__user=request.user)
    
    last_7_days = [timezone.now().date() - timedelta(days=x) for x in range(6, -1, -1)]
    scan_counts = (
        scans.filter(scan_time__date__in=last_7_days)
        .values('scan_time__date')
        .annotate(count=Count('id'))
        .order_by('scan_time__date')
    )
    scan_data = {str(day): 0 for day in last_7_days}
    for entry in scan_counts:
        scan_data[str(entry['scan_time__date'])] = entry['count']
    
    locations = (
        scans.values('city', 'country')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    return Response({
        'scan_data': scan_data,
        'locations': locations
    })