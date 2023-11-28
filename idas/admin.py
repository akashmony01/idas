from django.contrib import admin
from .models import Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'avatar', 'address']
    search_fields = ['user__username', 'first_name', 'last_name']


@admin.register(TimeSlotPreset)
class TimeSlotPresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'place', 'old_patient_fees', 'new_patient_fees', 'start_date', 'end_date', 'repeat_days')
    search_fields = ('name', 'place')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'preset')
    search_fields = ('title', 'preset__name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_type', 'appointment_date', 'appointment_slot')
    search_fields = ('patient_name', 'patient_type', 'appointment_date')
    list_filter = ('patient_type', 'appointment_date')


@admin.register(PatientFile)
class PatientFileAdmin(admin.ModelAdmin):
    list_display = ('file',)