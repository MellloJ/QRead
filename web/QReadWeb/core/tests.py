from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from core.models import QRCode, Scan
from core.serializers import QRCodeSerializer, ScanSerializer
import json
import uuid
from io import BytesIO
from django.core.files import File
import geoip2

CustomUser = get_user_model()

# Testes dos modelos
class TestQRCodeModel(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )

    def test_create_qrcode(self):
        """Testa a criação de um QRCode com dados válidos."""
        self.assertEqual(QRCode.objects.count(), 1)
        qrcode = QRCode.objects.first()
        self.assertEqual(qrcode.user, self.user)
        self.assertEqual(qrcode.content, 'https://qread.com')
        self.assertEqual(qrcode.short_url, 'qread123')
        self.assertIsNotNone(qrcode.created_at)
        self.assertIsInstance(qrcode.id, uuid.UUID)
        if qrcode.image and hasattr(qrcode.image, 'name') and qrcode.image.name:
            self.assertTrue(qrcode.image.name.startswith('qrcodes/qrcode-'))
    # @patch('core.models.QRCode')
    # def test_generate_qr_code(self, mock_qr_code):
    #     """Testa o método generate_qr_code."""
    #     mock_img = MagicMock()
    #     mock_img.save = MagicMock()
    #     mock_qr_instance = MagicMock()
    #     mock_qr_instance.make_image.return_value = mock_img
    #     mock_qr_code.return_value = mock_qr_instance

    #     qrcode = QRCode(
    #         user=self.user,
    #         content='https://qread.com/test',
    #         short_url='qread789'
    #     )
    #     qrcode.save()

    #     mock_qr_code.assert_called_once_with(
    #         version=1,
    #         error_correction=mock_qr_code.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4
    #     )
    #     mock_qr_instance.add_data.assert_called_once()
    #     mock_qr_instance.make.assert_called_once_with(fit=True)
    #     mock_img.save.assert_called_once()
    #     self.assertTrue(qrcode.image.name.startswith('qrcodes/qrcode-'))
    #     self.assertTrue(qrcode.image.name.startswith('qrcodes/qrcode-'))

    def test_get_absolute_url(self):
        """Testa o método get_absolute_url."""
        with self.settings(SITE_URL='http://localhost'):
            expected_url = f"http://localhost{reverse('core:qr_redirect', kwargs={'short_url': 'qread123'})}"
            self.assertEqual(self.qrcode.get_absolute_url(), expected_url)

    def test_save_generates_short_url(self):
        """Testa se o método save gera short_url automaticamente."""
        qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com/novo'
        )
        self.assertIsNotNone(qrcode.short_url)
        self.assertEqual(len(qrcode.short_url), 8)

    def test_short_url_unique(self):
        """Testa a restrição de unicidade do campo short_url."""
        with self.assertRaises(Exception):
            QRCode.objects.create(
                user=self.user,
                content='https://qread.com/outro',
                short_url='qread123'
            )

    def test_str_method(self):
        """Testa o método __str__."""
        self.assertEqual(str(self.qrcode), 'QR Code qread123 for https://qread.com')

class TestScanModel(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='192.168.1.1',
            city='São Paulo',
            country='Brasil'
        )

    def test_create_scan(self):
        """Testa a criação de um Scan com dados válidos."""
        self.assertEqual(Scan.objects.count(), 1)
        scan = Scan.objects.first()
        self.assertEqual(scan.qr_code, self.qrcode)
        self.assertEqual(scan.ip_address, '192.168.1.1')
        self.assertEqual(scan.city, 'São Paulo')
        self.assertEqual(scan.country, 'Brasil')
        self.assertIsNotNone(scan.scan_time)

    def test_str_method(self):
        """Testa o método __str__."""
        expected_str = f"Scan of QR Code qread123 for https://qread.com at {self.scan.scan_time}"
        self.assertEqual(str(self.scan), expected_str)

    def test_blank_city_country(self):
        """Testa criação de Scan com city e country vazios."""
        scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='10.0.0.1'
        )
        self.assertEqual(scan.city, '')
        self.assertEqual(scan.country, '')

# Testes das views
class TestDashboardView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('core:dashboard')
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='192.168.1.1',
            city='São Paulo',
            country='Brasil',
            scan_time=timezone.now()
        )

    def test_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertEqual(list(response.context['qrcodes']), [self.qrcode])
        self.assertEqual(list(response.context['scans']), [self.scan])
        scan_data = json.loads(response.context['scan_data'])
        self.assertEqual(len(scan_data), 7)  # 7 dias
        locations = response.context['locations']
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]['city'], 'São Paulo')
        self.assertEqual(locations[0]['country'], 'Brasil')
        self.assertEqual(locations[0]['count'], 1)

    # def test_get_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f'/accounts/login/?next={self.url}')

class TestPerfilView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('core:perfil')

    def test_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/perfil.html')

    # def test_get_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f'/accounts/login/?next={self.url}')

class TestConfiguracoesView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('core:configuracoes')

    def test_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/configuracoes.html')

    # def test_get_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f'/accounts/login/?next={self.url}')

class TestCreateQRCodeView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('core:create_qr_code')

    def test_get_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_qr_code.html')

    def test_post_valid_content(self):
        data = {'content': 'https://qread.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertEqual(QRCode.objects.count(), 1)
        qr_code = QRCode.objects.first()
        self.assertEqual(qr_code.content, 'https://qread.com')
        self.assertEqual(qr_code.user, self.user)

    def test_post_empty_content(self):
        data = {'content': ''}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/create_qr_code.html')
        self.assertEqual(QRCode.objects.count(), 0)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], 'Content is required.')

    # def test_get_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f'/accounts/login/?next={self.url}')

class TestQRRedirectView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.client = Client()
        self.url = reverse('core:qr_redirect', kwargs={'short_url': 'qread123'})

    @patch('geoip2.database.Reader')
    def test_get_valid_short_url(self, mock_reader):
        mock_response = MagicMock()
        mock_response.city.name = 'São Paulo'
        mock_response.country.name = 'Brasil'
        mock_reader.return_value.city.return_value = mock_response
        mock_reader.return_value.close = MagicMock()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, 'https://qread.com', fetch_redirect_response=False)
        self.assertEqual(Scan.objects.count(), 1)
        scan = Scan.objects.first()
        self.assertEqual(scan.qr_code, self.qrcode)
        self.assertEqual(scan.city, 'São Paulo')
        self.assertEqual(scan.country, 'Brasil')
        self.assertEqual(scan.ip_address, '127.0.0.1')

    @patch('geoip2.database.Reader')
    def test_get_invalid_ip(self, mock_reader):
        mock_reader.return_value.city.side_effect = geoip2.errors.AddressNotFoundError
        mock_reader.return_value.close = MagicMock()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, 'https://qread.com', fetch_redirect_response=False)
        self.assertEqual(Scan.objects.count(), 1)
        scan = Scan.objects.first()
        self.assertEqual(scan.city, 'Desconhecido')
        self.assertEqual(scan.country, 'Desconhecido')

    # def test_get_invalid_short_url(self):
    #     url = reverse('core:qr_redirect', kwargs={'short_url': 'invalid'})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 404)
    #     self.assertTemplateUsed(response, 'core/404.html')
    #     self.assertEqual(Scan.objects.count(), 0)

class TestQRCodeDetailsView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='192.168.1.1',
            city='São Paulo',
            country='Brasil',
            scan_time=timezone.now()
        )
        self.url = reverse('core:qr_code_details', kwargs={'short_url': 'qread123'})

    def test_get_authenticated_owner(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/qr_code_details.html')
        self.assertEqual(response.context['qr_code'], self.qrcode)
        self.assertEqual(list(response.context['scans']), [self.scan])
        scan_data = json.loads(response.context['scan_data'])
        self.assertEqual(len(scan_data), 7)
        locations = response.context['locations']
        self.assertEqual(len(locations), 1)
        self.assertEqual(locations[0]['city'], 'São Paulo')
        self.assertEqual(locations[0]['country'], 'Brasil')
        self.assertEqual(locations[0]['count'], 1)

    # def test_get_unauthenticated(self):
    #     self.client.logout()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_get_non_owner(self):
        other_user = CustomUser.objects.create_user(
            email='outro@qread.com',
            username='outro',
            password='QRead12345!'
        )
        self.client.force_login(other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

class TestLogoutView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('core:logout')

    # def test_get(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('core:dashboard'))
    #     self.assertFalse('_auth_user_id' in self.client.session)

class TestQRCodeViewSet(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.url = reverse('core:qrcode-list')

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'https://qread.com')

    # def test_create(self):
    #     data = {'content': 'https://qread.com/novo', 'short_url': 'qread456'}
    #     response = self.client.post(self.url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(QRCode.objects.count(), 2)
    #     self.assertEqual(QRCode.objects.last().content, 'https://qread.com/novo')
    #     self.assertEqual(QRCode.objects.last().user, self.user)

    def test_delete(self):
        detail_url = reverse('core:qrcode-detail', kwargs={'pk': self.qrcode.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(QRCode.objects.count(), 0)

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestScanViewSet(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='192.168.1.1',
            city='São Paulo',
            country='Brasil',
            scan_time=timezone.now()
        )
        self.url = reverse('core:scan-list')

    def test_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['city'], 'São Paulo')
        self.assertEqual(response.data[0]['country'], 'Brasil')

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestScanStatsView(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.qrcode = QRCode.objects.create(
            user=self.user,
            content='https://qread.com',
            short_url='qread123'
        )
        self.scan = Scan.objects.create(
            qr_code=self.qrcode,
            ip_address='192.168.1.1',
            city='São Paulo',
            country='Brasil',
            scan_time=timezone.now()
        )
        self.url = reverse('core:scan_stats', kwargs={'short_url': 'qread123'})
        self.global_url = reverse('core:scan_stats_global')

    # def test_get_all_scans(self):
    #     response = self.client.get(self.global_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     scan_data = response.data['scan_data']
    #     self.assertEqual(len(scan_data), 7)
    #     locations = response.data['locations']
    #     self.assertEqual(len(locations), 1)
    #     self.assertEqual(locations[0]['city'], 'São Paulo')
    #     self.assertEqual(locations[0]['country'], 'Brasil')
    #     self.assertEqual(locations[0]['count'], 1)

    # def test_get_invalid_short_url(self):
    #     url = reverse('core:scan_stats', kwargs={'short_url': 'invalid'})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_get_specific_qr_code(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     scan_data = response.data['scan_data']
    #     self.assertEqual(len(scan_data), 7)
    #     locations = response.data['locations']
    #     self.assertEqual(len(locations), 1)
    #     self.assertEqual(locations[0]['city'], 'São Paulo')
    #     self.assertEqual(locations[0]['country'], 'Brasil')
    #     self.assertEqual(locations[0]['count'], 1)

    # def test_get_unauthenticated(self):
    #     self.client.force_authenticate(user=None)
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)