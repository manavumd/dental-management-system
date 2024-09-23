from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets

from ..forms import ClinicForm, DoctorClinicAffiliationForm, DoctorScheduleFormSet
from ..models import Clinic, Doctor, DoctorClinicAffiliation, Visit, Appointment
from ..serializers import ClinicSerializer


# REST API ViewSets
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer


# Clinic CRUD
class ClinicListView(LoginRequiredMixin, ListView):
    model = Clinic
    template_name = 'administration/clinic_list.html'
    context_object_name = 'clinics'

    def get_queryset(self):
        # Prefetch doctor affiliations to avoid extra queries
        clinics = Clinic.objects.prefetch_related('doctorclinicaffiliation_set').all()

        for clinic in clinics:
            # Get doctors affiliated with the clinic
            affiliated_doctors = DoctorClinicAffiliation.objects.filter(clinic=clinic).values_list('doctor', flat=True)

            # Fetch patients from visits and appointments
            past_visits = Visit.objects.filter(clinic=clinic, doctor__in=affiliated_doctors).values_list('patient', flat=True)
            future_appointments = Appointment.objects.filter(
                clinic=clinic, 
                doctor__in=affiliated_doctors, 
                date_time__gte=datetime.now()
            ).values_list('patient', flat=True)

            # Combine and remove duplicates
            unique_patients = set(list(past_visits) + list(future_appointments))

            # Store the number of unique patients in the clinic object
            clinic.unique_patient_count = len(unique_patients)

        return clinics

class ClinicDetailView(LoginRequiredMixin, DetailView):
    model = Clinic
    template_name = 'administration/clinic_detail.html'

    context_object_name = 'clinic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all doctor affiliations for the current clinic
        affiliated_doctors = DoctorClinicAffiliation.objects.filter(clinic=self.object).values_list('doctor', flat=True)
        
        # Exclude doctors already affiliated with the clinic
        context['available_doctors'] = Doctor.objects.exclude(id__in=affiliated_doctors)
        
        # Add clinic affiliations to the context
        context['affiliations'] = DoctorClinicAffiliation.objects.filter(clinic=self.object)
        
        return context


def manage_affiliations(request, clinic_id, affiliation_id=None):
    print("manavTest")
    clinic = get_object_or_404(Clinic, id=clinic_id)
    
    # If editing an existing affiliation, fetch it
    if affiliation_id:
        affiliation = get_object_or_404(DoctorClinicAffiliation, id=affiliation_id)
        print("manavTest1")
        print(affiliation)
        available_doctors = Doctor.objects.filter(id=affiliation.doctor.id)  # Allow current doctor to be selected
    else:
        # Creating a new affiliation: Exclude doctors already affiliated with this clinic
        already_affiliated_doctors = DoctorClinicAffiliation.objects.filter(clinic=clinic).values_list('doctor', flat=True)
        available_doctors = Doctor.objects.exclude(id__in=already_affiliated_doctors)
        affiliation = DoctorClinicAffiliation(clinic=clinic)

    if request.method == 'POST':
        affiliation_form = DoctorClinicAffiliationForm(request.POST, instance=affiliation, available_doctors=available_doctors)
        schedule_formset = DoctorScheduleFormSet(request.POST, instance=affiliation, prefix='schedules')
        if affiliation_form.is_valid() and schedule_formset.is_valid():
            affiliation = affiliation_form.save(commit=False)
            affiliation.clinic = clinic
            affiliation.save()
            schedule_formset.instance = affiliation
            schedule_formset.save()

            return redirect('clinic_detail', pk=clinic_id)
        else:
            print("manavTest3")
            print(affiliation_form.errors)
            print(schedule_formset.errors)
    else:
        affiliation_form = DoctorClinicAffiliationForm(instance=affiliation, available_doctors=available_doctors)
        schedule_formset = DoctorScheduleFormSet(instance=affiliation, prefix='schedules')

    return render(request, 'administration/manage_affiliations.html', {'affiliation_form': affiliation_form,
        'schedule_formset': schedule_formset,
        'clinic_id': clinic_id,
        })

def remove_affiliation(request, affiliation_id):
    affiliation = get_object_or_404(DoctorClinicAffiliation, id=affiliation_id)
    affiliation.delete()
    return redirect('clinic_detail', pk=affiliation.clinic.id)

class ClinicCreateView(LoginRequiredMixin, CreateView):
    model = Clinic
    form_class = ClinicForm
    template_name = 'administration/clinic_form.html'
    success_url = reverse_lazy('clinic_list')

class ClinicUpdateView(LoginRequiredMixin, UpdateView):
    model = Clinic
    form_class = ClinicForm
    template_name = 'administration/clinic_form.html'
    success_url = reverse_lazy('clinic_list')

class ClinicDeleteView(LoginRequiredMixin, DeleteView):
    model = Clinic
    template_name = 'administration/clinic_confirm_delete.html'
    success_url = reverse_lazy('clinic_list')


def get_clinics(request):
    procedure_id = request.GET.get('procedure_id')
    
    # Get clinics that have doctors offering the selected procedure
    clinics = Clinic.objects.filter(
        doctorclinicaffiliation__doctor__specialties=procedure_id
    ).distinct()
    
    clinic_list = list(clinics.values('id', 'name'))
    return JsonResponse(clinic_list, safe=False)
