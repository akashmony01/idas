from django.shortcuts import render, redirect, HttpResponse
from .forms import (
    CustomSignupForm, TimeSlotPresetForm, TimeSlotFormSet,
    TimeSlotForm, AppointmentForm, PatientFileForm, PatientFileFormSet,
    DayOffForm, SiteInfoForm, ProfileForm, CollaboratorForm
)
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile, DayOff, SiteInfo
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from datetime import datetime
from .utils import is_superuser, is_staff, get_slots_by_date, is_slot_taken, is_day_off
from django.http import Http404
from django.db.models import Q
from django.core.mail import send_mail
today = date.today()



# Create your views here.
def not_found_404_view(request, exception):
    return render(request, '404.html', status=404)


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = CustomSignupForm()

    return render(request, 'registration/signup.html', {'form': form})


@user_passes_test(is_staff)
def dashboard_view(request):
    return render(request, 'idas/dashboard.html')

def home_view(request):
    return render(request, 'idas/index.html')


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    active_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date__gte=today,
        appointment_status='confirmed'
    ).order_by('appointment_date', 'appointment_slot')

    missed_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date__lt=today,
        appointment_status = 'confirmed'
    ).order_by('-appointment_date', '-appointment_slot')

    cancelled_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_status='cancelled'
    ).order_by('-appointment_date', '-appointment_slot')

    completed_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_status='completed'
    ).order_by('-appointment_date', '-appointment_slot')

    context = {
        'profile_form': ProfileForm(instance=profile),
        'avatar': profile.avatar,
        'active_appointments': active_appointments,
        'missed_appointments': missed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'completed_appointments': completed_appointments,
    }

    return render(request, 'idas/profile.html', context=context)


@login_required
def profile_update_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

    if profile_form.is_valid():
        profile_form.save()
        context = {
            "msg": "Profile Info updated!",
            "msg_color": "green",
            "profile_form": profile_form,
            'avatar': profile.avatar,
        }
    else:
        context = {
            "msg": "Something went wrong!",
            "msg_color": "red",
            "profile_form": profile_form,
            'avatar': profile.avatar,
        }

    return render(request, "idas/sub/profile_form.html", context)


@user_passes_test(is_superuser)
def site_info_view(request):
    site_info = get_object_or_404(SiteInfo, pk=1)

    print(site_info)

    context = { 'form': SiteInfoForm(instance=site_info) }
    return render(request, 'idas/site_info.html', context=context)


@user_passes_test(is_superuser)
@require_POST
def site_info_update_view(request):
    site_info = get_object_or_404(SiteInfo, pk=1)
    site_info_form = SiteInfoForm(request.POST, request.FILES, instance=site_info)

    if site_info_form.is_valid():
        site_info_form.save()
        context = {
            "msg": "Info updated!",
            "msg_color": "green",
            "form": site_info_form
        }
    else:
        context = {
            "msg": "Something went wrong!",
            "msg_color": "red",
            "form": site_info_form
        }

    return render(request, "idas/sub/site_info_form.html", context)


@user_passes_test(is_superuser)
def preset_create_view(request):
    if request.method == 'POST':
        form = TimeSlotPresetForm(request.POST)
        if form.is_valid():
            time_slot_preset = form.save()

            return redirect('preset_details', pk=time_slot_preset.pk)
    else:
        form = TimeSlotPresetForm()

    return render(request, 'idas/preset_create.html', {'form': form})


@user_passes_test(is_superuser)
def preset_details_view(request, pk):
    preset = get_object_or_404(TimeSlotPreset, pk=pk)
    slots = TimeSlot.objects.filter(preset=preset)

    context = {
        'preset_form': TimeSlotPresetForm(instance=preset),
        'update_slot_formset': TimeSlotFormSet(queryset=slots),
        'add_slot_form': TimeSlotForm,
        'preset_pk': preset.pk,
    }

    return render(request, 'idas/preset_details.html', context=context)


@user_passes_test(is_superuser)
@require_POST
def preset_update_view(request, pk):
    preset = get_object_or_404(TimeSlotPreset, pk=pk)
    preset_form = TimeSlotPresetForm(request.POST, instance=preset)

    if preset_form.is_valid():
        preset_form.save()

        context = {
            "preset_pk": preset.pk,
            "preset_form": preset_form,
            "msg": "Preset updated!",
            "msg_color": "green",
        }
    else:
        context = {
            "preset_pk": preset.pk,
            "preset_form": preset_form,
            "msg": "Something went wrong!",
            "msg_color": "red",
        }

    return render(request, "idas/sub/preset_update_form.html", context)


@user_passes_test(is_superuser)
@require_POST
def preset_slot_add_view(request, pk):
    preset = get_object_or_404(TimeSlotPreset, pk=pk)
    form = TimeSlotForm(request.POST)
    slots = TimeSlot.objects.filter(preset=preset)

    form.instance.preset = preset

    if form.is_valid():
        new_start_time = form.cleaned_data["start_time"]
        slot_exists = slots.filter(start_time=new_start_time).first()

        if slot_exists:
            error = "A slot already exists for this time."
            form.add_error("start_time", error)
            context = {
                'add_slot_form': form,
                'update_slot_formset': TimeSlotFormSet(queryset=slots),
                "msg": "This is slot already exists, try another one.",
                "msg_color": "red",
                "preset_pk": preset.pk,
            }
        else:
            form.save()
            context = {
                "add_slot_form": TimeSlotForm,
                'update_slot_formset': TimeSlotFormSet(queryset=slots),
                "msg": "Slot added!",
                "msg_color": "green",
                "preset_pk": preset.pk,
            }
    else:
        context = {
            "add_slot_form": form,
            'update_slot_formset': TimeSlotFormSet(queryset=slots),
            "msg": "Something went wrong try again.",
            "msg_color": "red",
            "preset_pk": preset.pk,
        }

    return render(request, "idas/sub/preset_slot_form.html", context=context)


@user_passes_test(is_superuser)
@require_POST
def preset_slot_update_view(request, pk):
    preset = get_object_or_404(TimeSlotPreset, pk=pk)
    slots = TimeSlot.objects.filter(preset=preset)
    formset = TimeSlotFormSet(request.POST)

    if formset.is_valid():
        errors_found = False

        for form in formset.forms:
            new_start_time = form.cleaned_data.get("start_time")
            slot_exists = slots.filter(start_time=new_start_time).first()

            if slot_exists and slot_exists.pk != form.instance.id:
                error = "A slot already exists for this time."
                form.add_error("start_time", error)
                errors_found = True
            else:
                form.save()

        if errors_found:
            context = {
                "add_slot_form": TimeSlotForm,
                "update_slot_formset": formset,
                "msg": "This item is already exists.",
                "msg_color": "red",
                "preset_pk": preset.pk,
            }
        else:
            context = {
                "add_slot_form": TimeSlotForm,
                "update_slot_formset": TimeSlotFormSet(queryset=slots),
                "preset_pk": preset.pk,
                "msg": "Slot updated",
                "msg_color": "green",
            }
    else:
        context = {
            "add_slot_form": TimeSlotForm,
            "update_slot_formset": formset,
            "msg": "Something went wrong",
            "msg_color": "red",
            "preset_pk": preset.pk,
        }

    return render(request, "idas/sub/preset_slot_form.html", context=context)


@user_passes_test(is_superuser)
@require_http_methods(["POST", "DELETE"])
def preset_slot_delete_view(request, preset_pk, slot_pk):
    preset = get_object_or_404(TimeSlotPreset, pk=preset_pk)
    slots = TimeSlot.objects.filter(preset=preset)
    item = TimeSlot.objects.get(pk=slot_pk)
    item.delete()
    context = {
        "add_slot_form": TimeSlotForm,
        "update_slot_formset": TimeSlotFormSet(queryset=slots),
        "msg": "Social item deleted successfully!",
        "msg_color": "green",
        "preset_pk": preset.pk,
    }

    return render(request, "idas/sub/preset_slot_form.html", context=context)


@user_passes_test(is_superuser)
def preset_list_view(request):
    active_preset = TimeSlotPreset.objects.filter(
        Q(end_date__gte=today) | (Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).exclude(Q(end_date__isnull=True) & Q(start_date__lt=today)).order_by('-end_date')

    previous_preset = TimeSlotPreset.objects.filter(
        ~Q(end_date__gte=today) & ~(Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).order_by('-end_date')

    context = {
        "active_preset": active_preset,
        "previous_preset": previous_preset
    }

    return render(request, "idas/preset_list.html", context=context)


@user_passes_test(is_superuser)
@require_http_methods(["POST", "DELETE"])
def preset_delete_view(request, pk):
    active_preset = TimeSlotPreset.objects.filter(
        Q(end_date__gte=today) | (Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).exclude(Q(end_date__isnull=True) & Q(start_date__lt=today)).order_by('-end_date')

    previous_preset = TimeSlotPreset.objects.filter(
        ~Q(end_date__gte=today) & ~(Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).order_by('-end_date')

    item = TimeSlotPreset.objects.get(pk=pk)

    item.delete()

    context = {
        "active_preset": active_preset,
        "previous_preset": previous_preset,
        "msg": "Preset is deleted successfully!",
        "msg_color": "red",
    }

    return render(request, "idas/sub/preset_list_inner.html", context=context)


@login_required
def appointment_get_view(request):
    target_date_param = request.GET.get('date')

    if target_date_param:
        target_date = datetime.strptime(target_date_param, '%Y-%m-%d').date()
        print(is_day_off(target_date))
        if target_date < today:
            context = {
                'past_date': True,
                'msg': 'Selected date is in the past.',
                'msg_color': 'red',
                'target_date': target_date,
                'heading': 'You choose a past date',
                'desc': 'please select a present or a future day, that will valid.'
            }
        else:
            print(is_day_off(target_date))

            if is_day_off(target_date):
                context = {
                    'day_off': True,
                    'target_date': target_date,
                    'heading': 'This is a day off!',
                    'desc': 'Doctor is not seeing any patient this particular day, try another one.'
                }
            else:
                time_slots = get_slots_by_date(target_date, by_preset=True)
                context = {
                    'target_date': target_date,
                    'time_slots': time_slots,
                }

    else:
        context = {
            'msg': 'Please choose a date first.',
            'msg_color': 'red',
        }

    return render(request, 'idas/appointment_get.html', context)


@login_required
def appointment_create_view(request, target_date, slot_pk):
    initial_time_slot = get_object_or_404(TimeSlot, pk=slot_pk)
    past_date = False
    invalid_slot = False
    slot_is_taken = False
    heading = ''
    desc = ''
    btn_text = ''

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        form.instance.user = request.user

        appointment_date = datetime.strptime(request.POST['appointment_date'], '%Y-%m-%d').date()
        appointment_slot = get_object_or_404(TimeSlot, pk=request.POST['appointment_slot'])

        valid_slot_list = get_slots_by_date(appointment_date)

        if is_slot_taken(appointment_date, appointment_slot):
            slot_is_taken = True
            heading = 'Appointment Exists!'
            desc = 'An appointment already exists for this slot. Please try another one.'
            btn_text = 'Please choose another time slot'
        if appointment_date < today:
            past_date = True
            heading = 'Past Date alert!'
            desc = 'You have chose a date in the past. Please try another date.'
            btn_text = 'Please choose another date'
        elif appointment_slot not in valid_slot_list:
            invalid_slot = True
            heading = 'Invalid appointment slot!'
            desc = 'This is not a valid slot for this date. Please try another one'
            btn_text = 'Please choose another time slot'
        else:
            if form.is_valid():
                appointment = form.save()
                return redirect('appointment_details', pk=appointment.pk)

    else:
        initial_data = {
            'appointment_date': target_date,
            'appointment_slot': initial_time_slot
        }

        form = AppointmentForm(initial=initial_data)

    context = {
        'heading': heading,
        'desc': desc,
        'btn_text': btn_text,
        'slot_is_taken': slot_is_taken,
        'past_date': past_date,
        'invalid_slot': invalid_slot,
        'appointment_date': target_date,
        'appointment_slot': initial_time_slot,
        'form': form
    }

    return render(request, 'idas/appointment_create.html', context=context)


@login_required
def appointment_details_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    files = PatientFile.objects.filter(appointment=appointment)

    if not request.user == appointment.user:
        raise Http404("You dont have permission.")

    if appointment.appointment_date < today or appointment.appointment_status == 'cancelled' or appointment.appointment_status == 'completed':
        patient_files = PatientFile.objects.filter(appointment=appointment)

        context = {
            'appointment_pk': appointment.pk,
            'appointment': appointment,
            'only_details': True,
            'patient_files': patient_files,
        }
    else:
        appointment_form = AppointmentForm(instance=appointment)

        context = {
            'appointment_form': appointment_form,
            'appointment_pk': appointment.pk,
            'appointment': appointment,
            'add_file_form': PatientFileForm,
            'update_file_form': PatientFileFormSet(queryset=files),
        }

    return render(request, 'idas/appointment_details.html', context=context)


@user_passes_test(is_superuser)
def appointment_list_view(request):
    active_appointments = Appointment.objects.filter(
        Q(appointment_date__gte=today) & (Q(appointment_status='confirmed') | Q(appointment_status='arrived'))
    ).order_by('appointment_date')

    completed_appointments = Appointment.objects.filter(Q(appointment_status='completed')).order_by('appointment_date')
    cancelled_appointments = Appointment.objects.filter(Q(appointment_status='cancelled')).order_by('appointment_date')

    missed_appointments = Appointment.objects.filter(
        Q(appointment_date__lt=today) & Q(appointment_status='confirmed')
    ).order_by('appointment_date')


    context = {
        "active_appointments": active_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "missed_appointments": missed_appointments,
    }

    return render(request, "idas/appointment_list.html", context=context)


@user_passes_test(is_staff)
def chamber_appointments_view(request):
    preset = request.user.profile.preset

    active_appointments = Appointment.objects.filter(
        Q(appointment_slot__preset=preset) &
        Q(appointment_date__gte=today) & (Q(appointment_status='confirmed') | Q(appointment_status='arrived'))
    ).order_by('appointment_date')

    completed_appointments = Appointment.objects.filter(Q(appointment_slot__preset=preset) & Q(appointment_status='completed')).order_by('appointment_date')
    cancelled_appointments = Appointment.objects.filter(Q(appointment_slot__preset=preset) & Q(appointment_status='cancelled')).order_by('appointment_date')

    missed_appointments = Appointment.objects.filter(
        Q(appointment_slot__preset=preset) &
        Q(appointment_date__lt=today) & Q(appointment_status='confirmed')
    ).order_by('appointment_date')


    context = {
        "active_appointments": active_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "missed_appointments": missed_appointments,
    }

    return render(request, "idas/appointment_list.html", context=context)


@user_passes_test(is_superuser)
def appointment_list_today_view(request):
    today_apps_not_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='confirmed').order_by('appointment_slot__start_time')
    today_apps_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='arrived').order_by('appointment_slot__start_time')

    context = {
        "today_apps_arrived": today_apps_arrived,
        "today_apps_not_arrived": today_apps_not_arrived,
    }

    return render(request, "idas/appointment_list_today.html", context=context)


@user_passes_test(is_superuser)
def appointments_by_day_view(request):
    pass

@user_passes_test(is_superuser)
def appointment_list_today_view(request):
    today_apps_not_arrived = Appointment.objects.filter(appointment_date=today,appointment_status='confirmed').order_by('appointment_slot__start_time')
    today_apps_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='arrived').order_by('appointment_slot__start_time')

    context = {
        "today_apps_arrived": today_apps_arrived,
        "today_apps_not_arrived": today_apps_not_arrived,
    }

    return render(request, "idas/appointment_list_today.html", context=context)


@user_passes_test(is_staff)
def chamber_appointments_today_view(request):
    preset = request.user.profile.preset

    today_apps_not_arrived = Appointment.objects.filter(
        appointment_slot__preset=preset,
        appointment_date=today,
        appointment_status='confirmed'
    ).order_by('appointment_slot__start_time')
    today_apps_arrived = Appointment.objects.filter(
        appointment_slot__preset=preset,
        appointment_date=today,
        appointment_status='arrived'
    ).order_by('appointment_slot__start_time')

    context = {
        "today_apps_arrived": today_apps_arrived,
        "today_apps_not_arrived": today_apps_not_arrived,
    }

    return render(request, "idas/appointment_list_today.html", context=context)


@user_passes_test(is_staff)
@require_POST
def appointment_mark_arrived_view(request, pk):
    item = get_object_or_404(Appointment, pk=pk)
    patient_files = PatientFile.objects.filter(appointment=item)
    is_reverse = request.GET.get('is_reverse', False)=='True'
    is_single = request.GET.get('is_single', False) == 'True'

    if is_reverse:
        item.appointment_status = 'confirmed'
    else:
        item.appointment_status = 'arrived'

    item.save()

    if is_single:
        context = {
            "appointment": item,
            "patient_files": patient_files,
        }
        return render(request, "idas/sub/appointment_view_inner.html", context=context)
    else:
        today_apps_not_arrived = Appointment.objects.filter(appointment_date=today,appointment_status='confirmed').order_by('appointment_slot__start_time')
        today_apps_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='arrived').order_by('appointment_slot__start_time')
        context = {
            "today_apps_arrived": today_apps_arrived,
            "today_apps_not_arrived": today_apps_not_arrived,
        }
        return render(request, "idas/sub/appointment_list_today_inner.html", context)


@user_passes_test(is_superuser)
@require_POST
def appointment_mark_completed_view(request, pk):
    item = get_object_or_404(Appointment, pk=pk)
    patient_files = PatientFile.objects.filter(appointment=item)
    is_single = request.GET.get('is_single', False) == 'True'
    doctor_note = request.POST.get('doctor_note')
    prescription = request.FILES.get('prescription')

    if doctor_note or prescription:
        item.doctor_note = doctor_note
        item.prescription = prescription
        item.appointment_status = 'completed'
        item.save()

        subject = 'Your appointment have been completed!'
        message = doctor_note
        from_email = 'admin@idas.com'
        recipient_list = [item.patient_email]
        send_mail(subject, message, from_email, recipient_list)

        if is_single:
            context = {
                "appointment": item,
                "patient_files": patient_files,
            }
            return render(request, "idas/sub/appointment_view_inner.html", context=context)
        else:
            today_apps_not_arrived = Appointment.objects.filter(appointment_date=today,appointment_status='confirmed').order_by('appointment_slot__start_time')
            today_apps_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='arrived').order_by('appointment_slot__start_time')
            context = {
                "today_apps_arrived": today_apps_arrived,
                "today_apps_not_arrived": today_apps_not_arrived,
            }
            return render(request, "idas/sub/appointment_list_today_inner.html", context)
    else:
        raise Http404("Could not find Prescription or Doctor Note!")


@user_passes_test(is_superuser)
@require_POST
def appointment_mark_cancelled_view(request, pk):
    item = get_object_or_404(Appointment, pk=pk)
    patient_files = PatientFile.objects.filter(appointment=item)
    cancel_note = request.POST.get('cancel_note')
    is_single = request.GET.get('is_single', False) == 'True'

    if cancel_note:
        item.cancel_note = cancel_note
        item.appointment_status = 'cancelled'
        item.save()

        subject = 'Your appointment have been cancelled!'
        message = cancel_note
        from_email = 'admin@idas.com'
        recipient_list = [item.patient_email]
        send_mail(subject, message, from_email, recipient_list)

        if is_single:
            context = {
                "appointment": item,
                "patient_files": patient_files,
            }
            return render(request, "idas/sub/appointment_view_inner.html", context=context)

        else:
            today_apps_not_arrived = Appointment.objects.filter(appointment_date=today,appointment_status='confirmed').order_by('appointment_slot__start_time')
            today_apps_arrived = Appointment.objects.filter(appointment_date=today, appointment_status='arrived').order_by('appointment_slot__start_time')
            context = {
                "today_apps_arrived": today_apps_arrived,
                "today_apps_not_arrived": today_apps_not_arrived,
            }
            return render(request, "idas/sub/appointment_list_today_inner.html", context)
    else:
        raise Http404("Could not find Cancel Note!")



@user_passes_test(is_staff)
def appointment_view_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    patient_files = PatientFile.objects.filter(appointment=appointment)

    print(patient_files)

    context = {
        "appointment": appointment,
        "patient_files": patient_files,
    }

    return render(request, "idas/appointment_view.html", context=context)


@login_required
@require_POST
def appointment_update_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if not request.user == appointment.user:
        raise Http404("You dont have permission.")

    if appointment.appointment_date < today:
        raise Http404("You cant edit past appointments.")

    appointment_form = AppointmentForm(request.POST, instance=appointment)

    if appointment_form.is_valid():
        appointment_form.save()

        context = {
            "appointment_pk": appointment.pk,
            "appointment_form": appointment_form,
            "msg": "appointment updated!",
            "msg_color": "green",
        }
    else:
        context = {
            "appointment_pk": appointment.pk,
            "appointment_form": appointment_form,
            "msg": "Something went wrong!",
            "msg_color": "red",
        }

    return render(request, "idas/sub/appointment_update_form.html", context)



@login_required
@require_http_methods(["POST", "DELETE"])
def appointment_delete_view(request, pk):
    item = Appointment.objects.get(pk=pk)

    if not request.user == item.user:
        raise Http404("You dont have permission.")

    active_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date__gte=today,
        appointment_status='confirmed'
    ).order_by('appointment_date', 'appointment_slot')

    missed_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_date__lt=today,
        appointment_status='confirmed'
    ).order_by('-appointment_date', '-appointment_slot')

    cancelled_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_status='cancelled'
    ).order_by('-appointment_date', '-appointment_slot')

    completed_appointments = Appointment.objects.filter(
        user=request.user,
        appointment_status='completed'
    ).order_by('-appointment_date', '-appointment_slot')

    item.delete()

    context = {
        "active_appointments": active_appointments,
        "missed_appointments": missed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "completed_appointments": completed_appointments,
        "msg": "Appointment is deleted successfully!",
        "msg_color": "green",
    }

    return render(request, "idas/sub/profile_appointment_list.html", context=context)


@login_required
@require_POST
def appointment_file_add_view(request, pk):
    appointment = Appointment.objects.get(pk=pk)

    if not request.user == appointment.user:
        raise Http404("You dont have permission.")

    form = PatientFileForm(request.POST, request.FILES)
    files = PatientFile.objects.filter(appointment=appointment)

    if form.is_valid():
        form.instance.appointment = appointment
        form.instance.user = request.user
        form.save()

        context = {
            "add_file_form": PatientFileForm,
            "appointment_pk": appointment.pk,
            'update_file_form': PatientFileFormSet(queryset=files),
            "msg": "File is added successfully!",
            "msg_color": "green",
        }

    return render(request, "idas/sub/appointment_file_form.html", context=context)


@login_required
@require_POST
def appointment_file_update_view(request, pk):
    appointment = Appointment.objects.get(pk=pk)

    if not request.user == appointment.user:
        raise Http404("You dont have permission.")

    files = PatientFile.objects.filter(appointment=appointment)
    formset = PatientFileFormSet(request.POST, request.FILES)

    if formset.is_valid():
        formset.save()
        context = {
            "add_file_form": PatientFileForm,
            "update_file_form": PatientFileFormSet(queryset=files),
            "appointment_pk": appointment.pk,
            "msg": "File is updated successfully!",
            "msg_color": "green",
        }
    else:
        context = {
            "add_file_form": PatientFileForm,
            "update_file_form": formset,
            "msg": "Something went wrong",
            "msg_color": "red",
            "appointment_pk": appointment.pk,
        }

    return render(request, "idas/sub/appointment_file_form.html", context=context)


@login_required
@require_http_methods(["POST", "DELETE"])
def appointment_file_delete_view(request, app_pk, file_pk):
    appointment = get_object_or_404(Appointment, pk=app_pk)

    if not request.user == appointment.user:
        raise Http404("You dont have permission.")

    files = PatientFile.objects.filter(appointment=appointment)
    item = PatientFile.objects.get(pk=file_pk)
    item.delete()
    context = {
        "add_file_form": PatientFileForm,
        "update_file_form": PatientFileFormSet(queryset=files),
        "msg": "File item deleted successfully!",
        "msg_color": "red",
        "appointment_pk": appointment.pk,
    }

    return render(request, "idas/sub/appointment_file_form.html", context=context)


@user_passes_test(is_superuser)
def day_off_create_view(request):
    if request.method == 'POST':
        form = DayOffForm(request.POST)
        if form.is_valid():
            day_off_instance = form.save(commit=False)

            if day_off_instance.end_date:
                overlapping_appointments = Appointment.objects.filter(
                    Q(appointment_date__range=[day_off_instance.start_date, day_off_instance.end_date]) |
                    Q(appointment_date=day_off_instance.start_date) |
                    Q(appointment_date=day_off_instance.end_date)
                )
            else:
                overlapping_appointments = Appointment.objects.filter(
                    Q(appointment_date=day_off_instance.start_date)
                )

            if overlapping_appointments.exists():
                for appointment in overlapping_appointments:
                    appointment.cancel_note = day_off_instance.desc_note
                    appointment.appointment_status = 'cancelled'
                    appointment.save()

                    subject = 'Your appointment have been cancelled!'
                    message = day_off_instance.desc_note
                    from_email = 'admin@idas.com'
                    recipient_list = [appointment.patient_email]
                    send_mail(subject, message, from_email, recipient_list)

            day_off_instance.save()
            return redirect('day_off_list')
    else:
        form = DayOffForm()

    return render(request, "idas/day_off_create.html", {'form': form})


@user_passes_test(is_superuser)
def day_off_list_view(request):
    active_dayoffs = DayOff.objects.filter(
        Q(end_date__gte=today) | (Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).exclude(Q(end_date__isnull=True) & Q(start_date__lt=today)).order_by('-end_date')

    previous_dayoffs = DayOff.objects.filter(
        ~Q(end_date__gte=today) & ~(Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).order_by('-end_date')

    context = {
        "active_dayoffs": active_dayoffs,
        "previous_dayoffs": previous_dayoffs
    }

    return render(request, "idas/day_off_list.html", context=context)


@user_passes_test(is_superuser)
@require_http_methods(["POST", "DELETE"])
def day_off_delete_view(request, pk):
    active_dayoffs = DayOff.objects.filter(
        Q(end_date__gte=today) | (Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).exclude(Q(end_date__isnull=True) & Q(start_date__lt=today)).order_by('-end_date')

    previous_dayoffs = DayOff.objects.filter(
        ~Q(end_date__gte=today) & ~(Q(end_date__isnull=True) & Q(start_date__gte=today))
    ).order_by('-end_date')

    item = DayOff.objects.get(pk=pk)

    item.delete()

    context = {
        "active_dayoffs": active_dayoffs,
        "previous_dayoffs": previous_dayoffs,
        "msg": "Day of item is deleted",
        "msg_color": "red",
    }

    return render(request, "idas/sub/day_off_list_inner.html", context=context)


@user_passes_test(is_superuser)
def day_off_details_view(request, pk):
    day_off_instance = get_object_or_404(DayOff, pk=pk)

    context = {
        'form': DayOffForm(instance=day_off_instance),
        'day_off_pk': day_off_instance.pk
    }

    return render(request, "idas/day_off_details.html", context=context)


@user_passes_test(is_superuser)
@require_POST
def day_off_update_view(request, pk):
    day_off = get_object_or_404(DayOff, pk=pk)
    day_off_form = DayOffForm(request.POST, instance=day_off)

    if day_off_form.is_valid():
        day_off_form.save()

        context = {
            "day_off_pk": day_off.pk,
            "form": day_off_form,
            "msg": "Day off data updated!",
            "msg_color": "green",
        }
    else:
        context = {
            "day_off_pk": day_off.pk,
            "form": day_off_form,
            "msg": "Something went wrong!",
            "msg_color": "red",
        }

    return render(request, "idas/sub/day_off_update_form.html", context)



@user_passes_test(is_superuser)
def collaborator_create_view(request):
    if request.method == 'POST':
        form = CollaboratorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('collaborator_list')  # Redirect to a success page or any other desired URL
    else:
        form = CollaboratorForm()

    return render(request, 'idas/collaborator_create.html', {'form': form})


@user_passes_test(is_superuser)
def collaborator_list_view(request):
    managers = User.objects.filter(is_staff=True, is_superuser=False)

    context = {
        "managers": managers
    }

    return render(request, 'idas/collaborator_list.html', context=context)



@user_passes_test(is_superuser)
def collaborator_delete_view(request, pk):
    item = get_object_or_404(User, pk=pk)
    item.delete()

    managers = User.objects.filter(is_staff=True, is_superuser=False)

    context = {
        "managers": managers,
        "msg": "Collaborator Deleted",
        "msg_color": "red"
    }

    return render(request, 'idas/sub/collaborator_list_inner.html', context=context)