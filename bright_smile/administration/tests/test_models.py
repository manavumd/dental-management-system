from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, time
from django.utils import timezone
from ..models import Clinic, Specialty, Doctor, DoctorClinicAffiliation, DoctorSchedule, Patient, Procedure, Visit, Appointment

class ClinicModelTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            phone_number="1234567890",
            city="Test City",
            state="Test State",
            email="testclinic@example.com"
        )

    def test_clinic_str(self):
        self.assertEqual(str(self.clinic), "Test Clinic")


class SpecialtyModelTest(TestCase):

    def setUp(self):
        self.specialty = Specialty.objects.create(name="Dentistry")

    def test_specialty_str(self):
        self.assertEqual(str(self.specialty), "Dentistry")


class DoctorModelTest(TestCase):

    def setUp(self):
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Test",
            email="doctor@example.com",
            phone_number="1234567890"
        )
        self.doctor.specialties.add(self.specialty)

    def test_doctor_str(self):
        self.assertEqual(str(self.doctor), "Dr. Test")

    def test_doctor_specialties(self):
        self.assertIn(self.specialty, self.doctor.specialties.all())


class DoctorClinicAffiliationModelTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            phone_number="1234567890",
            city="Test City",
            state="Test State",
            email="testclinic@example.com"
        )
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Test",
            email="doctor@example.com",
            phone_number="1234567890"
        )
        self.doctor.specialties.add(self.specialty)
        self.affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St."
        )

    def test_affiliation_str(self):
        self.assertEqual(str(self.affiliation), "Dr. Test at Test Clinic")


class DoctorScheduleModelTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            phone_number="1234567890",
            city="Test City",
            state="Test State",
            email="testclinic@example.com"
        )
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Test",
            email="doctor@example.com",
            phone_number="1234567890"
        )
        self.doctor.specialties.add(self.specialty)
        self.affiliation = DoctorClinicAffiliation.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            office_address="123 Clinic St."
        )
        self.schedule = DoctorSchedule.objects.create(
            affiliation=self.affiliation,
            day_of_week="Mon",
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

    def test_schedule_str(self):
        self.assertEqual(str(self.schedule), "Monday (09:00:00 - 17:00:00)")

    def test_schedule_validation(self):
        self.schedule.end_time = time(8, 0)
        with self.assertRaises(ValidationError):
            self.schedule.clean()


class PatientModelTest(TestCase):

    def setUp(self):
        self.patient = Patient.objects.create(
            name="John Doe",
            date_of_birth="1980-01-01",
            last_4_ssn="1234",
            phone_number="1234567890",
            gender="Male",
            address="123 Main St."
        )

    def test_patient_str(self):
        self.assertEqual(str(self.patient), "John Doe")


class ProcedureModelTest(TestCase):

    def setUp(self):
        self.procedure = Procedure.objects.create(name="Root Canal")

    def test_procedure_str(self):
        self.assertEqual(str(self.procedure), "Root Canal")


class VisitModelTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            phone_number="1234567890",
            city="Test City",
            state="Test State",
            email="testclinic@example.com"
        )
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Test",
            email="doctor@example.com",
            phone_number="1234567890"
        )
        self.doctor.specialties.add(self.specialty)
        self.patient = Patient.objects.create(
            name="John Doe",
            date_of_birth="1980-01-01",
            last_4_ssn="1234",
            phone_number="1234567890",
            gender="Male",
            address="123 Main St."
        )
        self.visit = Visit.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            clinic=self.clinic,
            date_time=timezone.now(),
            doctor_notes="Routine checkup"
        )
        self.visit.procedures_done.add(self.specialty)

    def test_visit_str(self):
        self.assertIn("Dr. Test", str(self.visit))


class AppointmentModelTest(TestCase):

    def setUp(self):
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            phone_number="1234567890",
            city="Test City",
            state="Test State",
            email="testclinic@example.com"
        )
        self.specialty = Specialty.objects.create(name="Dentistry")
        self.doctor = Doctor.objects.create(
            NPI="1234567890",
            name="Dr. Test",
            email="doctor@example.com",
            phone_number="1234567890"
        )
        self.doctor.specialties.add(self.specialty)
        self.patient = Patient.objects.create(
            name="John Doe",
            date_of_birth="1980-01-01",
            last_4_ssn="1234",
            phone_number="1234567890",
            gender="Male",
            address="123 Main St."
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            clinic=self.clinic,
            procedure=self.specialty,
            date_time=timezone.now()
        )

    def test_appointment_str(self):
        self.assertIn("Appointment on", str(self.appointment))
