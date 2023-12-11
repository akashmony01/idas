from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Assuming you have imported User model
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'address']


class TimeSlotPresetForm(forms.ModelForm):
    class Meta:
        model = TimeSlotPreset
        fields = ['name', 'place', 'old_patient_fees', 'new_patient_fees', 'start_date', 'end_date', 'repeat_days']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['title', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


TimeSlotFormSet = forms.modelformset_factory(
    TimeSlot,
    fields = ['title', 'start_time', 'end_time'],
    widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
    },
    extra=0
)


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'patient_name',
            'patient_gender',
            'patient_description',
            'patient_type',
            'patient_phone',
            'patient_email',
            'patient_address',
            'appointment_slot',
            'appointment_date',
            'appointment_status',
            'cancel_note',
            'doctor_note',
            'prescription',
        ]
        widgets = {
            'appointment_date': forms.HiddenInput(attrs={'readonly': 'readonly'}),
            'appointment_slot': forms.HiddenInput(attrs={'readonly': 'readonly'}),
            'appointment_status': forms.HiddenInput(attrs={'readonly': 'readonly'}),
        }



class PatientFileForm(forms.ModelForm):
    class Meta:
        model = PatientFile
        fields = ["name", "file"]


PatientFileFormSet = forms.modelformset_factory(
    PatientFile,
    fields=["name", "file"],
    extra=0
)