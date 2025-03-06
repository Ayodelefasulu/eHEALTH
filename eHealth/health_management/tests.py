from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from health_management.models import User, Patient, MedicalPractitioner, Appointment, Rating
from django.urls import reverse
from django.utils import timezone

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.patient_user = User.objects.create_user(
            email='patient@example.com', phone_number='1234567890', password='test123', is_patient=True
        )
        self.patient = Patient.objects.create(user=self.patient_user, name='Test Patient', date_of_birth='1990-01-01')
        self.practitioner_user = User.objects.create_user(
            email='doc@example.com', phone_number='0987654321', password='doc123', is_practitioner=True
        )
        self.practitioner = MedicalPractitioner.objects.create(
            user=self.practitioner_user, name='Dr. Test', specialization='General', location='City'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com', phone_number='1112223333', password='admin123'
        )

    def authenticate(self, email, password):
        response = self.client.post(reverse('login'), {'email': email, 'password': password}, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        return token

    # Test Login
    def test_login_success(self):
        response = self.client.post(reverse('login'), {'email': 'patient@example.com', 'password': 'test123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {'email': 'wrong@example.com', 'password': 'wrong'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Patient Registration
    def test_register_patient_success(self):
        data = {
            'user': {'email': 'newpatient@example.com', 'phone_number': '1112223334', 'password': 'new123', 'is_patient': True},
            'name': 'New Patient', 'date_of_birth': '1995-01-01'
        }
        response = self.client.post(reverse('register_patient'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_patient_duplicate_email(self):
        data = {
            'user': {'email': 'patient@example.com', 'phone_number': '1112223335', 'password': 'new123', 'is_patient': True},
            'name': 'Duplicate Patient', 'date_of_birth': '1995-01-01'
        }
        response = self.client.post(reverse('register_patient'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test Patient CRUD
    def test_patient_list_authenticated_patient(self):
        self.authenticate('patient@example.com', 'test123')
        response = self.client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patient_list_unauthenticated(self):
        response = self.client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test Appointment Creation
    def test_create_appointment_as_patient(self):
        self.authenticate('patient@example.com', 'test123')
        data = {
            'practitioner': self.practitioner.user.email,
            'date': timezone.now().isoformat()
        }
        response = self.client.post(reverse('appointment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_appointment_as_practitioner(self):
        self.authenticate('doc@example.com', 'doc123')
        data = {
            'practitioner': self.practitioner.user.email,
            'date': timezone.now().isoformat()
        }
        response = self.client.post(reverse('appointment-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test Rating
    def test_rate_practitioner_as_patient(self):
        self.authenticate('patient@example.com', 'test123')
        data = {
            'practitioner': self.practitioner.user.email,
            'rating': 5,
            'feedback': 'Great doctor!'
        }
        response = self.client.post(reverse('rate_practitioner'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rate_practitioner_as_non_patient(self):
        self.authenticate('doc@example.com', 'doc123')
        data = {
            'practitioner': self.practitioner.user.email,
            'rating': 5,
            'feedback': 'Great doctor!'
        }
        response = self.client.post(reverse('rate_practitioner'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
