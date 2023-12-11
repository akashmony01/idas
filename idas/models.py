from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator



class SingletonModel(models.Model):
    class Meta:
        abstract = True
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        pass

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Create your models here.
class Profile(TimeStampMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name+" "+self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.user.username

class TimeSlotPreset(TimeStampMixin):
    name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    old_patient_fees = models.DecimalField(max_digits=10, decimal_places=2)
    new_patient_fees = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    repeat_days = models.CharField(max_length=20, null=True, blank=True, help_text="Comma-separated list of days (e.g., 'mon,tue,thu')")

    def clean(self):
        # Validate that either start_date or repeat_days is provided
        if not (self.start_date or self.repeat_days):
            raise ValidationError("Either start_date or repeat_days must be provided.")

        # Validate that end_date is after start_date
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("End date must be after start date.")

        # Validate that start_date is not a past date and not today
        today = timezone.now().date()
        if self.start_date and (self.start_date < today or self.start_date == today):
            raise ValidationError("Start date must be at least tomorrow's date.")

        # Validate that old_patient_fees are less than or equal to new_patient_fees
        if self.old_patient_fees > self.new_patient_fees:
            raise ValidationError("Old patient fees must be less than or equal to new patient fees.")

    def __str__(self):
        return self.name


class TimeSlot(TimeStampMixin):
    title = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()
    preset = models.ForeignKey(TimeSlotPreset, on_delete=models.CASCADE, related_name='time_slots')

    def clean(self):
        # Validate that end_time is after start_time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        overlapping_slots = TimeSlot.objects.filter(
            preset=self.preset,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)  # Exclude self if instance is being updated

        if overlapping_slots.exists():
            raise ValidationError("A slot already exist for this time, please check again.")

    def __str__(self):
        return f"{self.title} - {self.start_time} to {self.end_time} ({self.preset})"


class Appointment(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('old', 'Old Patient'),
        ('new', 'New Patient'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    APPOINTMENT_STATUS = [
        ('confirmed', 'Confirmed'),
        ('arrived', 'Arrived'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255)
    patient_gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    patient_description = models.TextField(blank=True, null=True)
    patient_type = models.CharField(max_length=3, choices=PATIENT_TYPE_CHOICES)
    patient_phone = models.CharField(max_length=15)
    patient_email = models.EmailField()
    patient_address = models.TextField(blank=True, null=True)
    appointment_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_status = models.CharField(max_length=9, choices=APPOINTMENT_STATUS, default='confirmed')
    cancel_note = models.TextField(blank=True, null=True)
    doctor_note = models.TextField(blank=True, null=True)
    prescription = models.ImageField(
        upload_to='prescriptions/',
        blank=True, null=True,
        validators = [FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg', 'gif', 'pdf']
        )]
    )

    unique_together = ['appointment_date', 'appointment_slot']

    def clean(self):
        # Validate that appointment_date is not a past date
        today = timezone.now().date()
        if self.appointment_date and (self.appointment_date < today or self.appointment_date == today):
            raise ValidationError("Appointment date must be at least tomorrow's date.")

        # Validate the presence of cancel_note for 'cancelled' status
        if self.appointment_status == 'cancelled' and not self.cancel_note:
            raise ValidationError("Cancellation requires a cancellation note.")

        # Validate the presence of doctor_note and prescription for 'arrived' or 'completed' status
        if self.prescription and self.appointment_status in ['arrived', 'completed']:
            raise ValidationError("Prescription can be prescribed if the patient has arrived or the appointment is completed.")

        # Additional validation for unique appointment_date and appointment_slot
        conflicting_appointments = Appointment.objects.filter(
            appointment_date=self.appointment_date,
            appointment_slot=self.appointment_slot
        ).exclude(pk=self.pk)  # Exclude the current instance when checking for conflicts

        if conflicting_appointments.exists():
            raise ValidationError("An appointment with the same date and slot already exists. Please update the date or slot.")

    def __str__(self):
        return f"{self.patient_name} - {self.appointment_date}"



class PatientFile(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='patient_files')
    name = models.CharField(max_length=255)
    file = models.ImageField(upload_to='patient_files/')

    def __str__(self):
        return self.name