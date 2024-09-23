from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from ...models import Patient


class PatientViewTestCase(TestCase):
    def setUp(self):
        # Create a test user and log in
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Create test patients
        self.patient1 = Patient.objects.create(
            name='John Doe',
            date_of_birth='1990-01-01',
            last_4_ssn='1234',
            phone_number='555-555-5555',
            gender='Male',
            address='123 Main St'
        )
        self.patient2 = Patient.objects.create(
            name='Jane Doe',
            date_of_birth='1995-02-02',
            last_4_ssn='5678',
            phone_number='555-555-5556',
            gender='Female',
            address='456 Elm St'
        )

    def test_patient_list_view(self):
        # Test retrieving the patient list
        url = reverse('patient_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Doe')

    def test_patient_detail_view(self):
        # Test viewing patient details
        url = reverse('patient_detail', args=[self.patient1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_patient_create_view(self):
        # Test creating a new patient
        url = reverse('patient_create')
        data = {
            'name': 'Alice Smith',
            'date_of_birth': '2000-03-03',
            'last_4_ssn': '1111',
            'phone_number': '555-555-5557',
            'gender': 'Female',
            'address': '789 Oak St'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        self.assertEqual(Patient.objects.count(), 3)  # Should have 3 patients now

    def test_patient_update_view(self):
        # Test updating an existing patient
        url = reverse('patient_update', args=[self.patient1.id])
        data = {
            'name': 'John Doe Updated',
            'date_of_birth': '1990-01-01',
            'last_4_ssn': '1234',
            'phone_number': '555-555-5555',
            'gender': 'Male',
            'address': '123 Updated St'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        self.patient1.refresh_from_db()
        self.assertEqual(self.patient1.name, 'John Doe Updated')
        self.assertEqual(self.patient1.address, '123 Updated St')

    def test_patient_delete_view(self):
        # Test deleting a patient
        url = reverse('patient_delete', args=[self.patient1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful deletion
        self.assertEqual(Patient.objects.count(), 1)  # Only 1 patient should remain


class PatientViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test patients
        self.patient1 = Patient.objects.create(
            name='John Doe',
            date_of_birth='1990-01-01',
            last_4_ssn='1234',
            phone_number='555-555-5555',
            gender='Male',
            address='123 Main St'
        )
        self.patient2 = Patient.objects.create(
            name='Jane Doe',
            date_of_birth='1995-02-02',
            last_4_ssn='5678',
            phone_number='555-555-5556',
            gender='Female',
            address='456 Elm St'
        )

    def test_patient_list_api(self):
        # Test listing patients using API
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_patient_create_api(self):
        # Test creating a patient using API
        url = reverse('patient-list')
        data = {
            'name': 'Alice Smith',
            'date_of_birth': '2000-03-03',
            'last_4_ssn': '1111',
            'phone_number': '555-555-5557',
            'gender': 'Female',
            'address': '789 Oak St'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Patient.objects.count(), 3)


    def test_patient_delete_api(self):
        # Test deleting a patient using API
        url = reverse('patient-detail', args=[self.patient1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
