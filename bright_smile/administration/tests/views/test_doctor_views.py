from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from ...models import Doctor, Specialty


class DoctorViewTestCase(TestCase):
    def setUp(self):
        # Set up a user for login
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()

        # Login before running tests
        self.client.login(username='testuser', password='testpass')

        # Create some test specialties and doctors
        self.specialty1 = Specialty.objects.create(name='Dentist')
        self.specialty2 = Specialty.objects.create(name='Orthodontist')

        self.doctor = Doctor.objects.create(NPI="1234567890", name="John Doe", email="johndoe@example.com", phone_number="555-555-5555")
        self.doctor.specialties.add(self.specialty1)

    def test_doctor_list_view(self):
        # Test the doctor list page
        url = reverse('doctor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")

    def test_doctor_detail_view(self):
        # Test the doctor detail page
        url = reverse('doctor_detail', args=[self.doctor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")

    def test_doctor_create_view(self):
        # Test creating a new doctor
        url = reverse('doctor_create')
        data = {
            'NPI': '9876543210',
            'name': 'Jane Doe',
            'email': 'janedoe@example.com',
            'phone_number': '555-123-1234',
            'specialties': [self.specialty2.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertEqual(Doctor.objects.count(), 2)

    def test_doctor_update_view(self):
        # Test updating an existing doctor
        url = reverse('doctor_update', args=[self.doctor.id])
        data = {
            'NPI': self.doctor.NPI,
            'name': 'John Doe Updated',
            'email': 'johndoeupdated@example.com',
            'phone_number': '555-123-1234',
            'specialties': [self.specialty1.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.name, 'John Doe Updated')

    def test_doctor_delete_view(self):
        # Test deleting a doctor
        url = reverse('doctor_delete', args=[self.doctor.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        self.assertEqual(Doctor.objects.count(), 0)


class DoctorViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create some specialties and doctors
        self.specialty1 = Specialty.objects.create(name="Dentist")
        self.doctor = Doctor.objects.create(NPI="1234567890", name="John Doe", email="johndoe@example.com", phone_number="555-555-5555")
        self.doctor.specialties.add(self.specialty1)

    def test_doctor_list_api(self):
        # Test listing doctors using API
        url = reverse('doctor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_doctor_create_api(self):
        # Test creating a doctor using API
        url = reverse('doctor-list')
        data = {
            "NPI": "9876543210",
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "phone_number": "555-123-1234",
            "specialties": ["Dentist"]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Doctor.objects.count(), 2)


    def test_doctor_delete_api(self):
        # Test deleting a doctor using API
        url = reverse('doctor-detail', args=[self.doctor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
