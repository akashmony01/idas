from django.contrib import admin
from .models import SiteInfo, Speciality, WorkHistory, Qualification, Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile, DayOff


# Register your models here.
@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ['hero_subheading', 'hero_heading', 'hero_desc', 'hero_btn_1_text', 'hero_btn_2_text']


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


@admin.register(WorkHistory)
class WorkHistoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']


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
    list_display = ('name', 'file', 'user')


@admin.register(DayOff)
class DayOffAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'desc_note')