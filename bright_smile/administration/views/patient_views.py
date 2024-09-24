from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets

from ..forms import PatientForm
from ..models import Patient, Visit, Appointment
from ..serializers import PatientSerializer


# REST API ViewSets
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.none()
    serializer_class = PatientSerializer


# Patient CRUD
class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'administration/patient/patient_list.html'

    def get_queryset(self):
        patients = Patient.objects.all()

        # Add last visit and next appointment info to each patient
        for patient in patients:
            patient.last_visit = Visit.objects.filter(patient=patient).order_by('-date_time').first()
            patient.next_appointment = Appointment.objects.filter(patient=patient).order_by('date_time').first()

        print(patients)
        return patients

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'administration/patient/patient_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch patient's visit history and next appointment
        context['visits'] = Visit.objects.filter(patient=self.object).order_by('-date_time')
        context['appointments'] = Appointment.objects.filter(patient=self.object).order_by('date_time')

        return context

class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'administration/patient/patient_form.html'
    success_url = reverse_lazy('patient_list')

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'administration/patient/patient_form.html'
    success_url = reverse_lazy('patient_list')

class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = 'administration/patient/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')