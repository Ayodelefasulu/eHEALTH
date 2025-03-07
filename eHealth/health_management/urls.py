from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterPatientView,
    RegisterPractitionerView,
    LoginView,
    PatientViewSet,
    MedicalPractitionerViewSet,
    AppointmentViewSet,
    PractitionerRatingView)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'practitioners', MedicalPractitionerViewSet)
router.register(r'appointments', AppointmentViewSet)

urlpatterns = [
    path(
        '',
        include(
            router.urls)),
    path(
        'register/patient/',
        RegisterPatientView.as_view(),
        name='register_patient'),
    path(
        'register/practitioner/',
        RegisterPractitionerView.as_view(),
        name='register_practitioner'),
    path(
        'login/',
        LoginView.as_view(),
        name='login'),
    path(
        'rate-practitioner/',
        PractitionerRatingView.as_view(),
        name='rate_practitioner'),
]
