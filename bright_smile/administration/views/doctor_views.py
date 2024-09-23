from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets

from ..forms import DoctorForm
from ..models import Doctor, Patient, DoctorClinicAffiliation, Visit, Appointment
from ..serializers import DoctorSerializer


# REST API ViewSets
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.none()
    serializer_class = DoctorSerializer



# Doctor CRUD
class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor
    template_name = 'administration/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        doctors = Doctor.objects.prefetch_related('specialties', 'doctorclinicaffiliation_set').all()

        for doctor in doctors:
            # Fetch patients who visited this doctor
            past_visits = Visit.objects.filter(doctor=doctor).values_list('patient', flat=True)

            # Fetch patients who have future appointments with this doctor
            future_appointments = Appointment.objects.filter(doctor=doctor, date_time__gte=datetime.now()).values_list('patient', flat=True)

            # Combine and remove duplicates
            unique_patients = set(list(past_visits) + list(future_appointments))

            # Store the number of unique patients in the doctor object
            doctor.unique_patient_count = len(unique_patients)

        return doctors

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = 'administration/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch affiliations with clinics
        affiliations = DoctorClinicAffiliation.objects.filter(doctor=self.object).prefetch_related('schedules')
        context['affiliations'] = affiliations

        # Get the unique list of patients affiliated with the doctor (from visits or appointments)
        patients_from_visits = Patient.objects.filter(visits__doctor=self.object).distinct()
        patients_from_appointments = Patient.objects.filter(appointments__doctor=self.object).distinct()

        # Combine the two querysets and remove duplicates manually in Python
        all_patients = list(patients_from_visits) + list(patients_from_appointments)
        # Convert to a set of unique patient IDs to remove duplicates
        unique_patients = {patient.id: patient for patient in all_patients}.values()

        # Pass the unique patients to the context
        context['affiliated_patients'] = unique_patients
        
        return context

class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'administration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'administration/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

class DoctorDeleteView(LoginRequiredMixin, DeleteView):
    model = Doctor
    template_name = 'administration/doctor_confirm_delete.html'
    success_url = reverse_lazy('doctor_list')
