from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from ...models import Clinic, Doctor, Specialty, DoctorClinicAffiliation


class ClinicViewTests(TestCase):

    def setUp(self):
        # Create test client and test user
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Create a sample clinic for testing
        self.clinic = Clinic.objects.create(
            name='Test Clinic',
            phone_number='1234567890',
            city='Test City',
            state='Test State',
            email='clinic@test.com'
        )

        # Create specialties and doctors for testing
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(NPI='1234567890', name='Dr. Smith', email='dr.smith@test.com', phone_number='9876543210')
        self.doctor.specialties.add(self.specialty)

    def test_clinic_list_view(self):
        """ Test Clinic List View """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('clinic_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/clinic_list.html')
        self.assertContains(response, 'Test Clinic')

    def test_clinic_detail_view(self):
        """ Test Clinic Detail View """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('clinic_detail', args=[self.clinic.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'administration/clinic_detail.html')
        self.assertContains(response, 'Test Clinic')

    def test_clinic_create_view(self):
        """ Test Clinic Create View """
        self.client.login(username='testuser', password='12345')
        form_data = {
            'name': 'New Clinic',
            'phone_number': '0987654321',
            'city': 'New City',
            'state': 'New State',
            'email': 'newclinic@test.com',
        }
        response = self.client.post(reverse('clinic_create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after successful creation
        self.assertTrue(Clinic.objects.filter(name='New Clinic').exists())

    def test_clinic_update_view(self):
        """ Test Clinic Update View """
        self.client.login(username='testuser', password='12345')
        form_data = {
            'name': 'Updated Clinic',
            'phone_number': '0987654321',
            'city': 'Updated City',
            'state': 'Updated State',
            'email': 'updatedclinic@test.com',
        }
        response = self.client.post(reverse('clinic_update', args=[self.clinic.id]), data=form_data)
        self.assertEqual(response.status_code, 302)
        updated_clinic = Clinic.objects.get(id=self.clinic.id)
        self.assertEqual(updated_clinic.name, 'Updated Clinic')

    def test_clinic_delete_view(self):
        """ Test Clinic Delete View """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('clinic_delete', args=[self.clinic.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Clinic.objects.filter(id=self.clinic.id).exists())

    def test_get_clinics_api(self):
        """ Test get_clinics API View """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('get_clinics'), {'procedure_id': self.specialty.id})
        self.assertEqual(response.status_code, 200)

    def test_manage_affiliations(self):
        """ Test Manage Affiliations View """
        self.client.login(username='testuser', password='12345')
        form_data = {
            'doctor': self.doctor.id,
            'office_address': 'Test Address',
        }
        response = self.client.post(reverse('manage_affiliations', args=[self.clinic.id]), data=form_data)
        self.assertEqual(response.status_code, 200)

    def test_remove_affiliation(self):
        """ Test Remove Affiliation """
        self.client.login(username='testuser', password='12345')
        # Create an affiliation first
        affiliation = DoctorClinicAffiliation.objects.create(doctor=self.doctor, clinic=self.clinic, office_address='Test Address')
        response = self.client.post(reverse('remove_affiliation', args=[affiliation.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DoctorClinicAffiliation.objects.filter(id=affiliation.id).exists())
