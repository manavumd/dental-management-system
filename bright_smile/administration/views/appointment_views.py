from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..forms import AppointmentForm
from ..models import Doctor, Patient, DoctorClinicAffiliation, DoctorSchedule, Appointment


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
    appointment_date_obj = timezone.make_aware(datetime.strptime(appointment_date, '%Y-%m-%d'))
    day_of_week = appointment_date_obj.strftime('%a')

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

    appointment_duration = timedelta(minutes=15)

    # Initialize available slots based on doctor's working hours
    start_time = timezone.make_aware(datetime.combine(appointment_date_obj.date(), schedule.start_time))
    end_time = timezone.make_aware(datetime.combine(appointment_date_obj.date(), schedule.end_time))

    available_slots = []
    current_time = start_time

    booked_ranges = [
        (appointment.date_time, appointment.date_time + appointment_duration)
        for appointment in existing_appointments
    ]

    while current_time + appointment_duration <= end_time:
        is_conflict = False
        for start, end in booked_ranges:
            if start <= current_time < end:
                is_conflict = True
                break

        if not is_conflict:
            available_slots.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))

        current_time += appointment_duration

    if not available_slots:
        return JsonResponse({"error": "No available slots for the selected day"}, status=400)

    return JsonResponse(available_slots, safe=False)


def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    patient_id = appointment.patient.pk
    appointment.delete()
    return redirect('patient_detail', pk=patient_id)



def get_doctor_schedule(request):
    doctor_id = request.GET.get('doctor_id')
    clinic_id = request.GET.get('clinic_id')

    # Get the doctor's affiliation with the clinic
    affiliation = DoctorClinicAffiliation.objects.get(doctor_id=doctor_id, clinic_id=clinic_id)

    # Fetch the doctor's schedule for that clinic
    schedules = DoctorSchedule.objects.filter(affiliation=affiliation).values('day_of_week', 'start_time', 'end_time')

    schedule_list = list(schedules)
    return JsonResponse(schedule_list, safe=False)
