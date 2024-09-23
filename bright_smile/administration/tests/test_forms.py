from django.test import TestCase

from ..forms import ClinicForm, DoctorForm, PatientForm, VisitForm, AppointmentForm, DoctorClinicAffiliationForm
from ..models import Clinic, Doctor, Specialty, DoctorClinicAffiliation


class ClinicFormTest(TestCase):

    def test_clinic_form_valid(self):
        """ Test Clinic form with valid data """
        form = ClinicForm(data={
            'name': 'Test Clinic',
            'phone_number': '1234567890',
            'city': 'Test City',
            'state': 'Test State',
            'email': 'test@clinic.com'
        })
        self.assertTrue(form.is_valid())

    def test_clinic_form_invalid(self):
        """ Test Clinic form with invalid email """
        form = ClinicForm(data={
            'name': 'Test Clinic',
            'phone_number': '1234567890',
            'city': 'Test City',
            'state': 'Test State',
            'email': 'invalid-email'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn('email', form.errors)

class DoctorFormTest(TestCase):

    def setUp(self):
        self.specialty = Specialty.objects.create(name='Dentist')

    def test_doctor_form_valid(self):
        """ Test Doctor form with valid data """
        form = DoctorForm(data={
            'NPI': '1234567890',
            'name': 'Dr. Smith',
            'email': 'drsmith@clinic.com',
            'phone_number': '9876543210',
            'specialties': [self.specialty.id]
        })
        self.assertTrue(form.is_valid())

    def test_doctor_form_invalid(self):
        """ Test Doctor form with missing required fields """
        form = DoctorForm(data={
            'NPI': '',
            'name': '',
            'email': 'invalid-email',
            'phone_number': '9876543210',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('NPI', form.errors)
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)

class PatientFormTest(TestCase):

    def test_patient_form_valid(self):
        """ Test Patient form with valid data """
        form = PatientForm(data={
            'name': 'John Doe',
            'date_of_birth': '1990-01-01',
            'last_4_ssn': '1234',
            'phone_number': '1234567890',
            'gender': 'Male',
            'address': '123 Test Street'
        })
        self.assertTrue(form.is_valid())

    def test_patient_form_invalid(self):
        """ Test Patient form with missing required fields """
        form = PatientForm(data={
            'name': '',
            'date_of_birth': '',
            'last_4_ssn': '',
            'phone_number': '1234567890',
            'gender': '',
            'address': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('date_of_birth', form.errors)
        self.assertIn('last_4_ssn', form.errors)

class VisitFormTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(name='Test Clinic', phone_number='1234567890', city='Test City', state='Test State', email='test@clinic.com')
        self.specialty = Specialty.objects.create(name='Dentist')
        self.doctor = Doctor.objects.create(NPI='1234567890', name='Dr. Smith', email='drsmith@clinic.com', phone_number='9876543210')
        self.doctor.specialties.add(self.specialty)
        self.affiliation = DoctorClinicAffiliation.objects.create(doctor=self.doctor, clinic=self.clinic, office_address='Test Address')

    def test_visit_form_valid(self):
        """ Test Visit form with valid data """
        form = VisitForm(data={
            'clinic': self.clinic.id,
            'doctor': self.doctor.id,
            'date_time': '2024-01-01T10:00',
            'procedures_done': [self.specialty.id],
            'doctor_notes': 'Test notes'
        })
        self.assertTrue(form.is_valid())

    def test_visit_form_invalid(self):
        """ Test Visit form with missing required fields """
        form = VisitForm(data={
            'clinic': '',
            'doctor': '',
            'date_time': '',
            'procedures_done': [],
        })
        self.assertFalse(form.is_valid())
        self.assertIn('clinic', form.errors)
        self.assertIn('doctor', form.errors)
        self.assertIn('date_time', form.errors)

class AppointmentFormTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(name='Test Clinic', phone_number='1234567890', city='Test City', state='Test State', email='test@clinic.com')
        self.specialty = Specialty.objects.create(name='Dentist')
        self.doctor = Doctor.objects.create(NPI='1234567890', name='Dr. Smith', email='drsmith@clinic.com', phone_number='9876543210')
        self.doctor.specialties.add(self.specialty)
        self.affiliation = DoctorClinicAffiliation.objects.create(doctor=self.doctor, clinic=self.clinic, office_address='Test Address')

    def test_appointment_form_valid(self):
        """ Test Appointment form with valid data """
        form = AppointmentForm(data={
            'procedure': self.specialty.id,
            'clinic': self.clinic.id,
            'doctor': self.doctor.id,
            'date_time': '2024-01-01T10:00'
        })
        self.assertTrue(form.is_valid())

    def test_appointment_form_invalid(self):
        """ Test Appointment form with missing required fields """
        form = AppointmentForm(data={
            'procedure': '',
            'clinic': '',
            'doctor': '',
            'date_time': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('procedure', form.errors)
        self.assertIn('clinic', form.errors)
        self.assertIn('doctor', form.errors)
        self.assertIn('date_time', form.errors)

class DoctorClinicAffiliationFormTest(TestCase):

    def setUp(self):
        self.doctor = Doctor.objects.create(NPI='1234567890', name='Dr. Smith', email='drsmith@clinic.com', phone_number='9876543210')
        self.clinic = Clinic.objects.create(name='Test Clinic', phone_number='1234567890', city='Test City', state='Test State', email='test@clinic.com')

    def test_affiliation_form_valid(self):
        """ Test Affiliation form with valid data """
        form = DoctorClinicAffiliationForm(data={
            'doctor': self.doctor.id,
            'office_address': 'Test Office Address',
        }, available_doctors=Doctor.objects.all())
        self.assertTrue(form.is_valid())

    def test_affiliation_form_invalid(self):
        """ Test Affiliation form with missing fields """
        form = DoctorClinicAffiliationForm(data={
            'doctor': '',
            'office_address': ''
        }, available_doctors=Doctor.objects.all())
        self.assertFalse(form.is_valid())
        self.assertIn('doctor', form.errors)
        self.assertIn('office_address', form.errors)
