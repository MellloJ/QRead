from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from auth_app.models import CustomUser
from auth_app.serializers import RegisterSerializer, CustomTokenObtainPairSerializer

CustomUser = get_user_model()

# Testes do modelo CustomUser
class TestCustomUserModel(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'qreaduser@qread.com',
            'username': 'qreaduser',
            'password': 'QRead12345!',
            'name': 'QRead User',
            'is_active': True
        }
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_create_user(self):
        """Testa a criação de um usuário com dados válidos."""
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.first()
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_email_unique(self):
        """Testa a restrição de unicidade do campo email."""
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['username'] = 'differentuser'
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(**duplicate_user_data).full_clean()

    def test_username_unique(self):
        """Testa a restrição de unicidade do campo username."""
        duplicate_user_data = self.user_data.copy()
        duplicate_user_data['email'] = 'different@qread.com'
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(**duplicate_user_data).full_clean()

    def test_email_as_username_field(self):
        """Testa se o campo USERNAME_FIELD é 'email'."""
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')
        self.assertEqual(self.user.get_username(), self.user.email)

    def test_required_fields(self):
        """Testa se REQUIRED_FIELDS inclui 'username'."""
        self.assertEqual(CustomUser.REQUIRED_FIELDS, ['username'])

    def test_str_method(self):
        """Testa o método __str__ que retorna o email."""
        self.assertEqual(str(self.user), self.user.email)

    def test_create_user_without_email(self):
        """Testa a criação de um usuário sem email (deve falhar)."""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = ''
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(**invalid_data)

    def test_create_user_without_username(self):
        """Testa a criação de um usuário sem username (deve falhar)."""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = ''
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(**invalid_data)

    def test_create_superuser(self):
        """Testa a criação de um superusuário."""
        superuser = CustomUser.objects.create_superuser(
            email='admin@qread.com',
            username='admin',
            password='QReadAdmin123!'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.email, 'admin@qread.com')
        self.assertEqual(superuser.username, 'admin')
        self.assertTrue(superuser.check_password('QReadAdmin123!'))

    def test_meta_verbose_name(self):
        """Testa os metadados verbose_name e verbose_name_plural."""
        self.assertEqual(CustomUser._meta.verbose_name, 'User')
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'Users')

    def test_db_table(self):
        """Testa o nome da tabela no banco de dados."""
        self.assertEqual(CustomUser._meta.db_table, 'Users')

# Testes das views de autenticação
class TesteViewLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_app/login.html')

class TesteViewRegister(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_app/register.html')

class TesteRegisterView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register_api')

    def test_post_valid(self):
        data = {
            'email': 'qreaduser@qread.com',
            'password': 'QRead12345!',
            'username': 'qreaduser',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.first().email, 'qreaduser@qread.com')
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Usuário registrado com sucesso.')
        self.assertTrue(response.data['success'])

    def test_post_invalid(self):
        data = {
            'email': 'invalid',
            'password': 'weak',
            'username': '',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomUser.objects.count(), 0)

class TesteCustomTokenObtainPairView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.url = reverse('token_obtain_pair')

    def test_post_valid_credentials(self):
        data = {
            'email': 'qreaduser@qread.com',
            'password': 'QRead12345!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_post_invalid_credentials(self):
        data = {
            'email': 'qreaduser@qread.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

class TesteLoginWeb(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='qreaduser@qread.com',
            username='qreaduser',
            password='QRead12345!'
        )
        self.url = reverse('login_web')

    def test_post_valid_credentials(self):
        data = {
            'email': 'qreaduser@qread.com',
            'password': 'QRead12345!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'success', 'message': 'Login realizado com sucesso.'}
        )
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_post_invalid_credentials(self):
        data = {
            'email': 'qreaduser@qread.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'error', 'message': 'Usuário ou senha inválidos.'}
        )
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_post_missing_data(self):
        data = {
            'email': 'qreaduser@qread.com',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'status': 'error', 'message': 'Usuário ou senha inválidos.'}
        )