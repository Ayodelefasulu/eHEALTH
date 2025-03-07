from django.contrib import admin
from .models import User, Patient, MedicalPractitioner

# admin.site.register(User)
# admin.site.register(Patient)
# admin.site.register(MedicalPractitioner)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'phone_number',
        'is_patient',
        'is_practitioner',
        'is_staff',
        'is_superuser')
    list_filter = ('is_patient', 'is_practitioner', 'is_staff')
    search_fields = ('email', 'phone_number')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date_of_birth')
    search_fields = ('name', 'user__email')


@admin.register(MedicalPractitioner)
class MedicalPractitionerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'specialization', 'location')
    search_fields = ('name', 'user__email', 'specialization')
