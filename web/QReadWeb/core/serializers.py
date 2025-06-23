from rest_framework import serializers
from .models import QRCode, Scan

class QRCodeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = QRCode
        fields = ['id', 'content', 'short_url', 'image', 'created_at']

class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = ['qr_code', 'scan_time', 'ip_address', 'city', 'country']