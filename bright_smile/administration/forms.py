from django import forms
from django.forms import inlineformset_factory

from .models import Clinic, Doctor, Patient, DoctorClinicAffiliation, DAYS_OF_WEEK, DoctorSchedule, Specialty, Visit, \
    Appointment


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'phone_number', 'city', 'state', 'email']

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['NPI', 'name', 'email', 'phone_number', 'specialties']
        widgets = {
            'specialties': forms.CheckboxSelectMultiple(),
            # 'clinics': forms.CheckboxSelectMultiple(),
        }

class DoctorClinicAffiliationForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())

    class Meta:
        model = DoctorClinicAffiliation
        fields = ['doctor', 'office_address']

    def __init__(self, *args, **kwargs):
        available_doctors = kwargs.pop('available_doctors', Doctor.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = available_doctors


class DoctorScheduleForm(forms.ModelForm):
    day_of_week = forms.ChoiceField(choices=DAYS_OF_WEEK, widget=forms.Select)
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = DoctorSchedule
        fields = ['day_of_week', 'start_time', 'end_time']
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Check that the end time is after the start time
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'End time must be after start time.')
        
        return cleaned_data



# Inline formset for DoctorSchedule (related to DoctorClinicAffiliation)
DoctorScheduleFormSet = inlineformset_factory(
    DoctorClinicAffiliation,
    DoctorSchedule,
    form=DoctorScheduleForm,
    extra=0,  # Number of extra empty forms you want to display
    can_delete=True  # Allow the deletion of a schedule
)

class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('Male','Male'),('Female','Female')], widget=forms.Select)
    class Meta:
        model = Patient
        fields = ['name', 'date_of_birth', 'last_4_ssn', 'phone_number', 'gender', 'address']


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['clinic','doctor', 'date_time', 'procedures_done', 'doctor_notes']
        widgets = {
            'procedures_done': forms.CheckboxSelectMultiple(),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(VisitForm, self).__init__(*args, **kwargs)

        # Initially, doctors and procedures should be empty
        self.fields['doctor'].queryset = Doctor.objects.none()
        self.fields['procedures_done'].queryset = Specialty.objects.none()

        # When the form is submitted, filter based on the selected clinic and doctor
        if 'clinic' in self.data:
            try:
                clinic_id = int(self.data.get('clinic'))
                # Filter doctors based on the clinic using DoctorClinicAffiliation
                self.fields['doctor'].queryset = Doctor.objects.filter(
                    id__in=DoctorClinicAffiliation.objects.filter(clinic_id=clinic_id).values_list('doctor_id', flat=True)
                )
            except (ValueError, TypeError):
                pass  # Invalid clinic_id or doctor_id

        elif self.instance.pk:
            # Populate doctors if editing the visit
            self.fields['doctor'].queryset = Doctor.objects.filter(
                id__in=DoctorClinicAffiliation.objects.filter(clinic=self.instance.clinic).values_list('doctor_id', flat=True)
            )

        # When the doctor is selected, filter procedures based on the doctor's specialties
        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['procedures_done'].queryset = Doctor.objects.get(pk=doctor_id).specialties.all()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['procedures_done'].queryset = self.instance.doctor.specialties.all() 
   
class AppointmentForm(forms.ModelForm):
    procedure = forms.ModelChoiceField(queryset=Specialty.objects.all(), label="Select Procedure")

    class Meta:
        model = Appointment
        fields = ['procedure', 'clinic', 'doctor', 'date_time']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})  # Input type should match the format
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clinic'].queryset = Clinic.objects.none()
        self.fields['doctor'].queryset = Doctor.objects.none()

        # Dynamically update clinics and doctors based on the selected procedure
        if 'procedure' in self.data:
            try:
                procedure_id = int(self.data.get('procedure'))
                
                # Get clinics that have affiliated doctors offering this procedure
                self.fields['clinic'].queryset = Clinic.objects.filter(
                    doctorclinicaffiliation__doctor__specialties=procedure_id
                ).distinct()
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore it

        if 'clinic' in self.data:
            try:
                clinic_id = int(self.data.get('clinic'))
                procedure_id = int(self.data.get('procedure'))

                # Get doctors affiliated with the selected clinic and offering the procedure
                self.fields['doctor'].queryset = Doctor.objects.filter(
                    doctorclinicaffiliation__clinic=clinic_id,
                    specialties=procedure_id
                ).distinct()
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore it