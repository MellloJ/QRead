from django.db import models
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from django.conf import settings
from auth_app.models import CustomUser

class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='qrcodes')
    content = models.URLField(max_length=500)
    short_url = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='qrcodes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_qr_code(self):
        full_url = f"{settings.SITE_URL}{reverse('core:qr_redirect', kwargs={'short_url': self.short_url})}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qrcode-{self.id}.png'
        self.image.save(filename, File(buffer), save=False)

    def get_absolute_url(self):
        return f"{settings.SITE_URL}{reverse('core:qr_redirect', kwargs={'short_url': self.short_url})}"

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = str(uuid.uuid4())[:8]
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code {self.short_url} for {self.content}"

class Scan(models.Model):
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name='scans')
    scan_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Scan of {self.qr_code} at {self.scan_time}"