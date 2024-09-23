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



class SpecialityViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.none()
    serializer_class = SpecialtySerializer

