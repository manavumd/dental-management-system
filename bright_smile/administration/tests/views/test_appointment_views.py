from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from ...models import Clinic, Doctor, Patient, Appointment, Specialty, DoctorClinicAffiliation, DoctorSchedule


class AppointmentViewTestCase(TestCase):
    def setUp(self):
        # Setup test user and login
        self.client = Client()

        # Create test patient
        self.patient = Patient.objects.create(
            name="John Doe",
            date_of_birth="1990-01-01",
            last_4_ssn="1234",
            phone_number="555-555-5555",
            gender="Male",
            address="123 Main St."
        )

        # Create test clinic
        self.clinic = Clinic.objects.create(
            name="Bright Smile Clinic",
            phone_number="555-555-5556",
            city="New York",
            state="NY",
            email="clinic@example.com"
        )

        # Create test specialty
        self.specialty = Specialty.objects.create(name="Dentistry")

        # Create test doctor
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Smith",
            email="drsmith@example.com",
            phone_number="555-555-5557"
        )
        self.doctor.specialties.add(self.specialty)

        # Create doctor-clinic affiliation
        self.affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St."
        )

        # Create doctor schedule
        self.schedule = DoctorSchedule.objects.create(
            affiliation=self.affiliation,
            day_of_week="Mon",
            start_time="09:00:00",
            end_time="17:00:00"
        )

    def test_schedule_appointment(self):
        """Test scheduling an appointment for a patient."""
        url = reverse('schedule_appointment', args=[self.patient.id])
        data = {
            'procedure': self.specialty.id,
            'clinic': self.clinic.id,
            'doctor': self.doctor.id,
            'date_time': '2024-01-01T10:00:00'  # Format should match the input type
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful form submission
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        self.assertEqual(appointment.clinic, self.clinic)

    def test_get_available_slots(self):
        """Test fetching available slots for a doctor."""
        url = reverse('get_available_slots')
        appointment_date = '2024-09-02'  # Date in the future
        data = {
            'doctor_id': self.doctor.id,
            'clinic_id': self.clinic.id,
            'date': appointment_date
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('2024-09-02', response.json()[0])  # Check that the returned time slot includes the correct date

    def test_delete_appointment(self):
        """Test deleting an appointment."""
        # Create an appointment first
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            clinic=self.clinic,
            procedure=self.specialty,
            date_time="2024-01-01T10:00:00"
        )
        url = reverse('delete_appointment', args=[appointment.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_get_doctors_with_clinic_and_procedure(self):
        """Test retrieving doctors based on clinic and procedure."""
        url = reverse('get_doctors_with_clinic_and_procedure')
        data = {
            'clinic_id': self.clinic.id,
            'procedure_id': self.specialty.id
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], self.doctor.name)

    def test_get_doctor_schedule(self):
        """Test retrieving a doctor's schedule based on clinic."""
        url = reverse('get_doctor_schedule')
        data = {
            'doctor_id': self.doctor.id,
            'clinic_id': self.clinic.id
        }
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['day_of_week'], 'Mon')
        self.assertEqual(response.json()[0]['start_time'], '09:00:00')
        self.assertEqual(response.json()[0]['end_time'], '17:00:00')
