from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Clinic and Doctor-related models
class Clinic(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Specialty(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    NPI = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    specialties = models.ManyToManyField(Specialty, related_name='doctors')
    # clinics = models.ManyToManyField(Clinic, related_name='doctors')


    def __str__(self):
        return self.name

DAYS_OF_WEEK = [
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday'),
]

class DoctorClinicAffiliation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    office_address = models.TextField()

    def __str__(self):
        return f'{self.doctor.name} at {self.clinic.name}'
    
    def get_working_days_display(self):
        return ', '.join(self.working_days.split(','))

Doctor.clinics = models.ManyToManyField(Clinic, through=DoctorClinicAffiliation, related_name='affiliated_doctors')

class DoctorSchedule(models.Model):
    affiliation = models.ForeignKey(DoctorClinicAffiliation, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.get_day_of_week_display()} ({self.start_time} - {self.end_time})'
    
    def clean(self):
        """
        Ensure that the end time is greater than the start time.
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')

# Patient-related models
class Patient(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    last_4_ssn = models.CharField(max_length=4)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.name

class Procedure(models.Model):
    name = models.CharField(max_length=100)  # e.g., Cleaning, Root Canal

    def __str__(self):
        return self.name

class Visit(models.Model):
    patient = models.ForeignKey(Patient, related_name='visits', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='visits', on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, related_name='visits', on_delete=models.CASCADE)
    date_time = models.DateTimeField()  # Date and Time of the visit
    procedures_done = models.ManyToManyField(Specialty)  # Procedures done during the visit
    doctor_notes = models.TextField(blank=True)  # Notes from the doctor

    def __str__(self):
        return f'Visit on {self.date_time} by {self.doctor}'

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, related_name='appointments', on_delete=models.CASCADE)
    procedure = models.ForeignKey(Specialty, related_name='appointments', on_delete=models.CASCADE)
    date_time = models.DateTimeField()  # Date and Time of the appointment
    date_booked = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Appointment on {self.date_time} with {self.doctor}'
