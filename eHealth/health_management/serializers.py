"""
from rest_framework import serializers
from .models import User, Patient, MedicalPractitioner

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'is_patient', 'is_practitioner']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_patient=validated_data.get('is_patient', False),
            is_practitioner=validated_data.get('is_practitioner', False),
        )
        return user

class PatientSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()

    class Meta:
        model = Patient
        fields = ['user', 'name', 'date_of_birth']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class MedicalPractitionerSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()

    class Meta:
        model = MedicalPractitioner
        fields = ['user', 'name', 'specialization', 'location']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        practitioner = MedicalPractitioner.objects.create(user=user, **validated_data)
        return practitioner
"""

from rest_framework import serializers
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .models import User, Patient, MedicalPractitioner, Appointment, Rating

# 1. User Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'is_patient', 'is_practitioner']

    def validate(self, data):
        if data.get('is_patient') and data.get('is_practitioner'):
            raise ValidationError("A user cannot be both a patient and a practitioner.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_patient=validated_data.get('is_patient', False),
            is_practitioner=validated_data.get('is_practitioner', False),
        )
        # Send email invitation for practitioners
        if validated_data.get('is_practitioner'):
            send_mail(
                subject="Join Our Medical Platform",
                message=f"Dear {validated_data['email']},\nYou’ve been invited to join as a Medical Practitioner. Register at: [your-url]",
                from_email='admin@ehealth.com',
                recipient_list=[validated_data['email']],
                fail_silently=True,
            )
        return user

# 2. Login Serializer (Authentication)
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                raise ValidationError("This account is inactive.")
            return {'user': user}
        raise ValidationError("Invalid email or password.")

# 3. Patient Serializer (Full CRUD)
class PatientSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()

    class Meta:
        model = Patient
        fields = ['user', 'name', 'date_of_birth']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserRegistrationSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        instance.name = validated_data.get('name', instance.name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.save()
        return instance

# 4. Medical Practitioner Serializer (Full CRUD)
class MedicalPractitionerSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()

    class Meta:
        model = MedicalPractitioner
        fields = ['user', 'name', 'specialization', 'location']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserRegistrationSerializer().create(user_data)
        practitioner = MedicalPractitioner.objects.create(user=user, **validated_data)
        return practitioner

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserRegistrationSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        instance.name = validated_data.get('name', instance.name)
        instance.specialization = validated_data.get('specialization', instance.specialization)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance

# 5. Appointment Serializer (Appointment Management)
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'practitioner', 'date', 'status']
        read_only_fields = ['patient']  # Patient set automatically from request.user

    def validate(self, data):
        if data['practitioner'].user.is_practitioner is False:
            raise ValidationError("Selected practitioner is not a valid medical practitioner.")
        if self.context['request'].user.is_patient is False:
            raise ValidationError("Only patients can book appointments.")
        return data

    def create(self, validated_data):
        # Automatically set patient to the requesting user
        validated_data['patient'] = self.context['request'].user.patient
        return Appointment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Allow cancellation by patient or status change by practitioner
        user = self.context['request'].user
        if user.is_patient and validated_data.get('status') == 'cancelled':
            instance.status = 'cancelled'
        elif user.is_practitioner and user.medicalpractitioner == instance.practitioner:
            instance.status = validated_data.get('status', instance.status)
        else:
            raise ValidationError("Permission denied to update this appointment.")
        instance.save()
        return instance

class PractitionerRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['practitioner', 'rating', 'feedback']

    def validate(self, data):
        if self.context['request'].user.is_patient is False:
            raise ValidationError("Only patients can rate practitioners.")
        return data

    def create(self, validated_data):
        return Rating.objects.create(
            patient=self.context['request'].user.patient,
            **validated_data
        )
