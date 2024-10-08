from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from ..forms import VisitForm
from ..models import Doctor, Patient, DoctorClinicAffiliation, Visit


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


def get_doctors(request):
    clinic_id = request.GET.get('clinic_id')
    doctors = DoctorClinicAffiliation.objects.filter(clinic_id=clinic_id).select_related('doctor').values('doctor__id', 'doctor__name')
    return JsonResponse(list(doctors), safe=False)

def get_specialties(request):
    doctor_id = request.GET.get('doctor_id')
    specialties = Doctor.objects.get(pk=doctor_id).specialties.values('id', 'name')
    return JsonResponse(list(specialties), safe=False)


def delete_visit(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    patient_id = visit.patient.pk  # Save the patient's ID to redirect back after deletion
    visit.delete()
    return redirect('patient_detail', pk=patient_id)
