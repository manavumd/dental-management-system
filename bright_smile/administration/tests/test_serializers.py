from django.test import TestCase

from ..models import Clinic, Doctor, Patient, Specialty
from ..serializers import ClinicSerializer, DoctorSerializer, PatientSerializer, SpecialtySerializer


class ClinicSerializerTest(TestCase):

    def setUp(self):
        self.clinic_data = {
            'name': 'Test Clinic',
            'phone_number': '1234567890',
            'city': 'Test City',
            'state': 'Test State',
            'email': 'test@clinic.com'
        }

    def test_clinic_serializer_valid(self):
        """ Test ClinicSerializer with valid data """
        serializer = ClinicSerializer(data=self.clinic_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['name'], 'Test Clinic')

    def test_clinic_serializer_invalid(self):
        """ Test ClinicSerializer with invalid data """
        self.clinic_data['email'] = 'invalid-email'
        serializer = ClinicSerializer(data=self.clinic_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_clinic_serializer_serialization(self):
        """ Test ClinicSerializer serialization """
        clinic = Clinic.objects.create(**self.clinic_data)
        serializer = ClinicSerializer(clinic)
        self.assertEqual(serializer.data['name'], 'Test Clinic')
        self.assertEqual(serializer.data['phone_number'], '1234567890')

class SpecialtySerializerTest(TestCase):

    def setUp(self):
        self.specialty = Specialty.objects.create(name='Dentistry')

    def test_specialty_serializer(self):
        """ Test SpecialtySerializer serialization """
        serializer = SpecialtySerializer(self.specialty)
        self.assertEqual(serializer.data['name'], 'Dentistry')

    def test_specialty_serializer_deserialization(self):
        """ Test SpecialtySerializer deserialization """
        specialty_data = {'name': 'Orthodontics'}
        serializer = SpecialtySerializer(data=specialty_data)
        self.assertTrue(serializer.is_valid())
        specialty = serializer.save()
        self.assertEqual(specialty.name, 'Orthodontics')

class DoctorSerializerTest(TestCase):

    def setUp(self):
        self.specialty1 = Specialty.objects.create(name='Dentistry')
        self.specialty2 = Specialty.objects.create(name='Orthodontics')
        self.doctor_data = {
            'NPI': '1234567890',
            'name': 'Dr. Smith',
            'email': 'drsmith@clinic.com',
            'phone_number': '9876543210',
            'specialties': [self.specialty1.name, self.specialty2.name]
        }

    def test_doctor_serializer_valid(self):
        """ Test DoctorSerializer with valid data """
        serializer = DoctorSerializer(data=self.doctor_data)
        self.assertTrue(serializer.is_valid())
        doctor = serializer.save()
        self.assertEqual(doctor.name, 'Dr. Smith')
        self.assertEqual(doctor.specialties.count(), 2)

    def test_doctor_serializer_invalid(self):
        """ Test DoctorSerializer with missing required fields """
        self.doctor_data['NPI'] = ''  # NPI is required
        serializer = DoctorSerializer(data=self.doctor_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('NPI', serializer.errors)

    def test_doctor_serializer_serialization(self):
        """ Test DoctorSerializer serialization """
        doctor = Doctor.objects.create(NPI='1234567890', name='Dr. Smith', email='drsmith@clinic.com', phone_number='9876543210')
        doctor.specialties.set([self.specialty1, self.specialty2])
        serializer = DoctorSerializer(doctor)
        self.assertEqual(serializer.data['name'], 'Dr. Smith')
        self.assertEqual(len(serializer.data['specialties']), 2)

class PatientSerializerTest(TestCase):

    def setUp(self):
        self.patient_data = {
            'name': 'John Doe',
            'date_of_birth': '1990-01-01',
            'last_4_ssn': '1234',
            'phone_number': '1234567890',
            'gender': 'Male',
            'address': '123 Test Street'
        }

    def test_patient_serializer_valid(self):
        """ Test PatientSerializer with valid data """
        serializer = PatientSerializer(data=self.patient_data)
        self.assertTrue(serializer.is_valid())
        patient = serializer.save()
        self.assertEqual(patient.name, 'John Doe')
        self.assertEqual(patient.phone_number, '1234567890')

    def test_patient_serializer_invalid(self):
        """ Test PatientSerializer with missing required fields """
        self.patient_data['name'] = ''  # Name is required
        serializer = PatientSerializer(data=self.patient_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_patient_serializer_serialization(self):
        """ Test PatientSerializer serialization """
        patient = Patient.objects.create(**self.patient_data)
        serializer = PatientSerializer(patient)
        self.assertEqual(serializer.data['name'], 'John Doe')
        self.assertEqual(serializer.data['last_4_ssn'], '1234')
