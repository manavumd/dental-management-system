from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from .models import Clinic, Doctor, Patient, DoctorClinicAffiliation, DoctorSchedule, Visit, Appointment, Specialty
from .forms import ClinicForm, DoctorForm, PatientForm, DoctorClinicAffiliationForm, DoctorScheduleFormSet, VisitForm, AppointmentForm
from .serializers import ClinicSerializer, DoctorSerializer, PatientSerializer, SpecialtySerializer
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin



# REST API ViewSets
class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.none()
    serializer_class = ClinicSerializer

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.none()
    serializer_class = DoctorSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.none()
    serializer_class = PatientSerializer

class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.none()
    serializer_class = SpecialtySerializer

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

# Patient CRUD
class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'administration/patient_list.html'

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
    template_name = 'administration/patient_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch patient's visit history and next appointment
        context['visits'] = Visit.objects.filter(patient=self.object).order_by('-date_time')
        context['appointments'] = Appointment.objects.filter(patient=self.object).order_by('date_time')

        return context

class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'administration/patient_form.html'
    success_url = reverse_lazy('patient_list')

class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'administration/patient_form.html'
    success_url = reverse_lazy('patient_list')

class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = 'administration/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')


def add_visit(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient
            visit.save()
            form.save_m2m()  # Save Many-to-Many fields (procedures_done)
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = VisitForm()

    return render(request, 'administration/add_visit.html', {'form': form, 'patient': patient})


def schedule_appointment(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        print(form.errors)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.save()
            return redirect('patient_detail', pk=patient_id)
    else:
        form = AppointmentForm()

    return render(request, 'administration/schedule_appointment.html', {'form': form, 'patient': patient})


def get_doctors(request):
    clinic_id = request.GET.get('clinic_id')
    doctors = DoctorClinicAffiliation.objects.filter(clinic_id=clinic_id).select_related('doctor').values('doctor__id', 'doctor__name')
    return JsonResponse(list(doctors), safe=False)

def get_specialties(request):
    doctor_id = request.GET.get('doctor_id')
    specialties = Doctor.objects.get(pk=doctor_id).specialties.values('id', 'name')
    return JsonResponse(list(specialties), safe=False)

def get_clinics(request):
    procedure_id = request.GET.get('procedure_id')
    
    # Get clinics that have doctors offering the selected procedure
    clinics = Clinic.objects.filter(
        doctorclinicaffiliation__doctor__specialties=procedure_id
    ).distinct()
    
    clinic_list = list(clinics.values('id', 'name'))
    return JsonResponse(clinic_list, safe=False)

def get_doctors_with_clinic_and_procedure(request):
    clinic_id = request.GET.get('clinic_id')
    procedure_id = request.GET.get('procedure_id')

    # Get doctors affiliated with the selected clinic who offer the selected procedure
    doctors = Doctor.objects.filter(
        doctorclinicaffiliation__clinic=clinic_id,
        specialties=procedure_id
    ).distinct()

    doctor_list = list(doctors.values('id', 'name'))
    return JsonResponse(doctor_list, safe=False)

def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    clinic_id = request.GET.get('clinic_id')
    appointment_date = request.GET.get('date')  # Expected format: YYYY-MM-DD

    # Convert the appointment_date to a datetime object and get the day of the week
    appointment_date_obj = timezone.make_aware(datetime.strptime(appointment_date, '%Y-%m-%d'))  # Aware datetime
    day_of_week = appointment_date_obj.strftime('%a')  # Mon, Tue, Wed, etc.

    # Fetch the doctor's schedule for the specific clinic and day
    affiliation = DoctorClinicAffiliation.objects.get(doctor_id=doctor_id, clinic_id=clinic_id)
    schedule = DoctorSchedule.objects.filter(affiliation=affiliation, day_of_week=day_of_week).first()

    if not schedule:
        return JsonResponse({"error": "Doctor is not available on the selected day"}, status=400)

    # Fetch existing appointments for the doctor at this clinic on the selected date
    existing_appointments = Appointment.objects.filter(
        doctor_id=doctor_id,
        clinic_id=clinic_id,
        date_time__date=appointment_date_obj.date()
    )

    # Define appointment slot duration
    appointment_duration = timedelta(minutes=15)

    # Initialize available slots based on doctor's working hours
    start_time = timezone.make_aware(datetime.combine(appointment_date_obj.date(), schedule.start_time))
    end_time = timezone.make_aware(datetime.combine(appointment_date_obj.date(), schedule.end_time))

    available_slots = []
    current_time = start_time

    # List existing appointments as time ranges for easy comparison
    booked_ranges = [
        (appointment.date_time, appointment.date_time + appointment_duration)
        for appointment in existing_appointments
    ]

    # Generate slots while checking for conflicts with existing appointments
    while current_time + appointment_duration <= end_time:
        is_conflict = False
        for start, end in booked_ranges:
            if start <= current_time < end:
                is_conflict = True
                break

        if not is_conflict:
            available_slots.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))  # Full datetime format

        # Move to the next time slot
        current_time += appointment_duration

    if not available_slots:
        return JsonResponse({"error": "No available slots for the selected day"}, status=400)

    return JsonResponse(available_slots, safe=False)


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    patient_id = appointment.patient.pk  # Save the patient's ID to redirect back after deletion
    appointment.delete()
    return redirect('patient_detail', pk=patient_id)

def delete_visit(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    patient_id = visit.patient.pk  # Save the patient's ID to redirect back after deletion
    visit.delete()
    return redirect('patient_detail', pk=patient_id)

def get_doctor_schedule(request):
    doctor_id = request.GET.get('doctor_id')
    clinic_id = request.GET.get('clinic_id')

    # Get the doctor's affiliation with the clinic
    affiliation = DoctorClinicAffiliation.objects.get(doctor_id=doctor_id, clinic_id=clinic_id)

    # Fetch the doctor's schedule for that clinic
    schedules = DoctorSchedule.objects.filter(affiliation=affiliation).values('day_of_week', 'start_time', 'end_time')

    schedule_list = list(schedules)  # Convert QuerySet to a list of dictionaries
    return JsonResponse(schedule_list, safe=False)
