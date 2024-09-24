from django.contrib import admin
from .models import Clinic, Doctor, Patient, Specialty

admin.site.register(Clinic)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Specialty)
