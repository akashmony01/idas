# Generated by Django 4.2.7 on 2023-11-15 23:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("idas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="email",
            field=models.EmailField(default="example@email.com", max_length=254),
            preserve_default=False,
        ),
    ]
