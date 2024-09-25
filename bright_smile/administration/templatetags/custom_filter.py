from django import template
from itertools import groupby
from operator import attrgetter

register = template.Library()

@register.filter
def total_patients(doctors):
    return sum(doctor.patients.count() for doctor in doctors)

@register.filter
def unique_doctors(affiliations):
    """
    Takes a QuerySet of DoctorClinicAffiliation and returns a list of unique doctors.
    """
    unique_doctor_ids = set()
    unique_doctors = []

    for affiliation in affiliations:
        if affiliation.doctor.id not in unique_doctor_ids:
            unique_doctor_ids.add(affiliation.doctor.id)
            unique_doctors.append(affiliation.doctor)

    return unique_doctors

@register.filter
def unique_clinics(affiliations):
    """
    Takes a QuerySet of DoctorClinicAffiliation and returns a list of unique clinics.
    """
    unique_clinic_ids = set()
    unique_clinics = []

    for affiliation in affiliations:
        if affiliation.clinic.id not in unique_clinic_ids:
            unique_clinic_ids.add(affiliation.clinic.id)
            unique_clinics.append(affiliation.clinic)

    return unique_clinics

@register.filter
def group_by_day(schedules):
    """
    Group schedules by the 'day_of_week' attribute.
    Returns a dictionary where the key is the day of the week and the value is a list of schedules.
    """

    DAY_ORDER = {
        'Mon': 1,
        'Tue': 2,
        'Wed': 3,
        'Thu': 4,
        'Fri': 5,
        'Sat': 6,
        'Sun': 7
    }
    schedules = sorted(schedules, key=lambda s: DAY_ORDER.get(s.day_of_week, 8))

    # Group the schedules by day_of_week
    grouped_schedules = {}
    for key, group in groupby(schedules, key=attrgetter('day_of_week')):
        grouped_schedules[key] = list(group)
    
    return grouped_schedules.items()