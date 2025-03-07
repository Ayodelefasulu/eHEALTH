# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.permissions import [
    IsAuthenticated, AllowAny, BasePermission
]
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Patient, MedicalPractitioner, Appointment
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    PatientSerializer,
    MedicalPractitionerSerializer,
    AppointmentSerializer,
    PractitionerRatingSerializer)

# Custom Permissions


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_patient


class IsPractitioner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_practitioner


class IsPatientOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            request.user.is_patient and obj.user == request.user)


class IsPractitionerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            request.user.is_practitioner and obj.user == request.user)

# 1. Registration Views


class RegisterPatientView(generics.CreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]


class RegisterPractitionerView(generics.CreateAPIView):
    serializer_class = MedicalPractitionerSerializer
    permission_classes = [AllowAny]

# 2. Login View (Authentication)


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'email': user.email},
                        status=status.HTTP_200_OK)

# 3. Patient CRUD


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'date_of_birth']

    def get_queryset(self):
        try:
            if self.request.user.is_patient:
                return Patient.objects.filter(user=self.request.user)
            elif self.request.user.is_practitioner or self.request.user.is_staff:
                return Patient.objects.all()
            return Patient.objects.none()
        except Exception:
            return Patient.objects.none()

# 4. Medical Practitioner CRUD (with Search/Filtering)


class MedicalPractitionerViewSet(viewsets.ModelViewSet):
    queryset = MedicalPractitioner.objects.all()
    serializer_class = MedicalPractitionerSerializer
    permission_classes = [IsAuthenticated, IsPractitionerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['specialization', 'location', 'name']
    search_fields = ['name', 'specialization', 'location']
    ordering_fields = ['name', 'specialization']
    ordering = ['name']

    def get_queryset(self):
        if self.request.user.is_practitioner:
            return MedicalPractitioner.objects.select_related(
                'user').filter(user=self.request.user)
        return MedicalPractitioner.objects.select_related('user').all()

# 5. Appointment Management


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [IsPatient()]
        elif self.action in ['update', 'partial_update']:
            # return [IsAuthenticated()]
            return [IsPatient(), IsPractitioner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Appointment.objects.filter(patient=user.patient)
        elif user.is_practitioner:
            return Appointment.objects.filter(
                practitioner=user.medicalpractitioner)
        elif user.is_staff:
            return Appointment.objects.all()
        return Appointment.objects.none()


class PractitionerRatingView(generics.CreateAPIView):
    serializer_class = PractitionerRatingSerializer
    permission_classes = [IsPatient]
