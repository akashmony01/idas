from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SiteInfo, Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile, DayOff

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Assuming you have imported User model
        fields = ['username', 'email', 'password1', 'password2']


class CollaboratorForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True, )
    preset = forms.ModelChoiceField(queryset=TimeSlotPreset.objects.all(), required=True, label='Chamber')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.preset = self.cleaned_data.get('preset')
            profile.save()

        return user



class SiteInfoForm(forms.ModelForm):
    class Meta:
        model = SiteInfo
        fields = '__all__'


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


class DayOffForm(forms.ModelForm):
    class Meta:
        model = DayOff
        fields = ["title", "start_date", "end_date", "desc_note"]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }