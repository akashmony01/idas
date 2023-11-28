# Generated by Django 4.2.7 on 2023-11-17 22:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("idas", "0013_remove_appointment_patient_files_delete_patientfile"),
    ]

    operations = [
        migrations.CreateModel(
            name="PatientFile",
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
                (
                    "file",
                    models.FileField(
                        upload_to="patient_files/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["png", "jpg", "jpeg", "gif", "pdf"]
                            )
                        ],
                    ),
                ),
                (
                    "appointment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="patient_files",
                        to="idas.appointment",
                    ),
                ),
            ],
        ),
    ]
