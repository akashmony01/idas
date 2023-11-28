# Generated by Django 4.2.7 on 2023-11-17 22:04

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("idas", "0010_alter_timeslot_end_time_alter_timeslot_start_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="timeslotpreset",
            old_name="fees",
            new_name="new_patient_fees",
        ),
        migrations.AddField(
            model_name="timeslotpreset",
            name="old_patient_fees",
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("patient_name", models.CharField(max_length=255)),
                (
                    "patient_gender",
                    models.CharField(
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                        ],
                        max_length=6,
                    ),
                ),
                ("patient_description", models.TextField(blank=True, null=True)),
                (
                    "patient_type",
                    models.CharField(
                        choices=[("old", "Old Patient"), ("new", "New Patient")],
                        max_length=3,
                    ),
                ),
                ("patient_phone", models.CharField(max_length=15)),
                ("patient_email", models.EmailField(max_length=254)),
                ("patient_address", models.TextField(blank=True, null=True)),
                (
                    "patient_files",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="patient_files/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["png", "jpg", "jpeg", "gif", "pdf"]
                            )
                        ],
                    ),
                ),
                ("appointment_date", models.DateField()),
                (
                    "appointment_slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="idas.timeslot"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]