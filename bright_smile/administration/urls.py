from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .baseviews import (    
    SpecialityViewSet
)
from .views.clinic_views import ClinicListView, ClinicDetailView, ClinicCreateView, ClinicUpdateView, ClinicDeleteView,manage_affiliations, remove_affiliation,ClinicViewSet, get_clinics
from .views.doctor_views import DoctorListView, DoctorDetailView, DoctorCreateView, DoctorUpdateView, DoctorDeleteView,DoctorViewSet
from .views.patient_views import PatientListView, PatientDetailView, PatientCreateView, PatientUpdateView, PatientDeleteView, PatientViewSet
from .views.visit_views import add_visit,get_doctors, get_specialties,delete_visit
from .views.appointment_views import schedule_appointment, get_doctors_with_clinic_and_procedure, get_available_slots, delete_appointment, get_doctor_schedule

from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r'api/clinics', ClinicViewSet, basename='clinic')
router.register(r'api/doctors', DoctorViewSet, basename='doctor')
router.register(r'api/patients', PatientViewSet, basename='patient')
router.register(r'api/specialties', SpecialityViewSet, basename='specialty')

urlpatterns = [

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='administration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Clinic URLs
    path('clinics/', ClinicListView.as_view(), name='clinic_list'),
    path('clinics/create/', ClinicCreateView.as_view(), name='clinic_create'),
    path('clinics/<int:pk>/', ClinicDetailView.as_view(), name='clinic_detail'),
    path('clinics/<int:pk>/update/', ClinicUpdateView.as_view(), name='clinic_update'),
    path('clinics/<int:pk>/delete/', ClinicDeleteView.as_view(), name='clinic_delete'),

    path('clinics/<int:pk>/', ClinicDetailView.as_view(), name='clinic_detail'),
    path('clinics/<int:pk>/edit/', ClinicUpdateView.as_view(), name='clinic_update'),
    path('clinics/<int:clinic_id>/affiliations/', manage_affiliations, name='manage_affiliations'),
    path('clinics/<int:clinic_id>/affiliations/<int:affiliation_id>/', manage_affiliations, name='edit_affiliation'),

    path('affiliations/remove/<int:affiliation_id>/', remove_affiliation, name='remove_affiliation'),

    # Doctor URLs
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctors/create/', DoctorCreateView.as_view(), name='doctor_create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctors/<int:pk>/update/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctors/<int:pk>/delete/', DoctorDeleteView.as_view(), name='doctor_delete'),

    # Patient URLs
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/create/', PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/update/', PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),

    path('patients/<int:patient_id>/visit/add/', add_visit, name='add_visit'),
    path('patients/<int:patient_id>/appointment/schedule/', schedule_appointment, name='schedule_appointment'),

    path('api/get-doctors/', get_doctors, name='get_doctors'),
    path('api/get-specialties/', get_specialties, name='get_specialties'),
    path('api/get-clinics/', get_clinics, name='get_clinics'),
    path('api/get-doctors-with-clinic-and-procedure/', get_doctors_with_clinic_and_procedure, name='get_doctors_with_clinic_and_procedure'),
    path('api/get-available-slots/', get_available_slots, name='get_available_slots'),
    path('api/get-doctor-schedule/', get_doctor_schedule, name='get_doctor_schedule'),

    path('appointments/delete/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
    path('visit/delete/<int:visit_id>/', delete_visit, name='delete_visit'),

    path('', include(router.urls)),

]
