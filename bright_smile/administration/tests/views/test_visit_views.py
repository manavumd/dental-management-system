from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from ...models import Patient, Doctor, Clinic, Visit, Specialty, DoctorClinicAffiliation


class VisitViewTestCase(TestCase):
    def setUp(self):
        # Set up test user and login
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Create test models
        self.patient = Patient.objects.create(
            name='John Doe',
            date_of_birth='1990-01-01',
            last_4_ssn='1234',
            phone_number='555-555-5555',
            gender='Male',
            address='123 Main St'
        )

        self.clinic = Clinic.objects.create(
            name='Bright Smile Clinic',
            phone_number='555-555-5556',
            city='New York',
            state='NY',
            email='clinic@example.com'
        )

        self.specialty = Specialty.objects.create(name='Dentistry')
        self.doctor = Doctor.objects.create(
            NPI='1234567890',
            name='Dr. Smith',
            email='drsmith@example.com',
            phone_number='555-555-5557'
        )
        self.doctor.specialties.add(self.specialty)

        # Create affiliation between the doctor and clinic
        self.affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address='123 Clinic St.'
        )

    def test_add_visit(self):
        # Test adding a visit
        url = reverse('add_visit', args=[self.patient.id])
        data = {
            'clinic': self.clinic.id,
            'doctor': self.doctor.id,
            'date_time': '2023-09-22T10:00:00',  # Date and time of the visit
            'procedures_done': [self.specialty.id],
            'doctor_notes': 'Check-up was successful.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertEqual(Visit.objects.count(), 1)
        visit = Visit.objects.first()
        self.assertEqual(visit.patient, self.patient)
        self.assertEqual(visit.doctor, self.doctor)
        self.assertEqual(visit.clinic, self.clinic)
        self.assertEqual(visit.doctor_notes, 'Check-up was successful.')

    def test_delete_visit(self):
        # Test deleting a visit
        visit = Visit.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            clinic=self.clinic,
            date_time='2023-09-22T10:00:00'
        )
        url = reverse('delete_visit', args=[visit.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertEqual(Visit.objects.count(), 0)

    def test_get_doctors(self):
        # Test retrieving doctors for a specific clinic
        url = reverse('get_doctors') + f'?clinic_id={self.clinic.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['doctor__name'], 'Dr. Smith')

    def test_get_specialties(self):
        # Test retrieving specialties for a specific doctor
        url = reverse('get_specialties') + f'?doctor_id={self.doctor.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'Dentistry')

