from rest_framework import serializers
from .models import Clinic, Doctor, Patient, Specialty

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):

    # specialties = serializers.StringRelatedField(many=True)
    specialties = serializers.SlugRelatedField(queryset=Specialty.objects.all(), many=True, slug_field='name')


    class Meta:
        model = Doctor
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
