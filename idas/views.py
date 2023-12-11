from django.shortcuts import render, redirect, HttpResponse
from .forms import (
    CustomSignupForm, TimeSlotPresetForm, TimeSlotFormSet,
    TimeSlotForm, AppointmentForm, PatientFileForm, PatientFileFormSet
)
from django.contrib.auth import login
from .models import Profile, TimeSlotPreset, TimeSlot, Appointment, PatientFile
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
from datetime import datetime
from .utils import get_slots_by_date, is_slot_taken



# Create your views here.
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


def home_view(request):
    return render(request, 'idas/index.html')


@login_required
def profile_view(request):
    return render(request, 'idas/profile.html')


@user_passes_test(lambda user: user.is_staff)
def preset_create_view(request):
    if request.method == 'POST':
        form = TimeSlotPresetForm(request.POST)
        if form.is_valid():
            time_slot_preset = form.save()

            return redirect('preset_details', pk=time_slot_preset.pk)
    else:
        form = TimeSlotPresetForm()

    return render(request, 'idas/preset_create.html', {'form': form})


@user_passes_test(lambda user: user.is_staff)
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


@user_passes_test(lambda user: user.is_staff)
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


@user_passes_test(lambda user: user.is_staff)
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


@user_passes_test(lambda user: user.is_staff)
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


@user_passes_test(lambda user: user.is_staff)
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


@user_passes_test(lambda user: user.is_staff)
def preset_list_view(request):
    preset_list = TimeSlotPreset.objects.all().order_by('-created_at')

    context = {
        "presets": preset_list,
    }

    return render(request, "idas/preset_list.html", context=context)


@user_passes_test(lambda user: user.is_staff)
@require_http_methods(["POST", "DELETE"])
def preset_delete_view(request, pk):
    preset_list = TimeSlotPreset.objects.all().order_by('-created_at')
    item = TimeSlotPreset.objects.get(pk=pk)

    item.delete()

    context = {
        "presets": preset_list,
        "msg": "Preset is deleted successfully!",
        "msg_color": "green",
    }

    return render(request, "idas/sub/preset_list_inner.html", context=context)


@login_required
def appointment_get_view(request):
    target_date_param = request.GET.get('date')

    if target_date_param:
        target_date = datetime.strptime(target_date_param, '%Y-%m-%d').date()

        today = date.today()
        if target_date < today:
            context = {
                'past_date': True,
                'msg': 'Selected date is in the past.',
                'msg_color': 'red',
                'target_date': target_date,
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


def appointment_create_view(request, target_date, slot_pk):
    initial_time_slot = get_object_or_404(TimeSlot, pk=slot_pk)
    past_date = False
    invalid_slot = False
    slot_is_taken = False

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        form.instance.user = request.user

        appointment_date = datetime.strptime(request.POST['appointment_date'], '%Y-%m-%d').date()
        appointment_slot = get_object_or_404(TimeSlot, pk=request.POST['appointment_slot'])

        valid_slot_list = get_slots_by_date(appointment_date)
        today = date.today()

        if is_slot_taken(appointment_date, appointment_slot):
            slot_is_taken = True
        if appointment_date < today:
            past_date = True
        elif appointment_slot not in valid_slot_list:
            invalid_slot = True
        else:
            if form.is_valid():
                form.save()
                return redirect('home')

    else:
        initial_data = {
            'appointment_date': target_date,
            'appointment_slot': initial_time_slot
        }

        form = AppointmentForm(initial=initial_data)

    context = {
        'slot_is_taken': slot_is_taken,
        'past_date': past_date,
        'invalid_slot': invalid_slot,
        'appointment_date': target_date,
        'appointment_slot': initial_time_slot,
        'form': form
    }

    return render(request, 'idas/appointment_create.html', context=context)


def appointment_details_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    files = PatientFile.objects.filter(appointment=appointment)
    appointment_form = AppointmentForm(instance=appointment)

    context = {
        'appointment_form': appointment_form,
        'appointment_pk': appointment.pk,
        'add_file_form': PatientFileForm,
        'update_file_form': PatientFileFormSet(queryset=files),
    }

    return render(request, 'idas/appointment_details.html', context=context)


@user_passes_test(lambda user: user.is_staff)
def appointment_list_view(request):
    appointment_list = Appointment.objects.all().order_by('-appointment_date')

    context = {
        "appointment_list": appointment_list,
    }

    return render(request, "idas/appointment_list.html", context=context)


@login_required
@require_POST
def appointment_update_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
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
    appointment_list = Appointment.objects.all().order_by('-appointment_date')
    item = Appointment.objects.get(pk=pk)

    item.delete()

    context = {
        "appointment_list": appointment_list,
        "msg": "Appointment is deleted successfully!",
        "msg_color": "green",
    }

    return render(request, "idas/sub/appointment_list_inner.html", context=context)


@login_required
@require_POST
def appointment_file_add_view(request, pk):
    appointment = Appointment.objects.get(pk=pk)
    form = PatientFileForm(request.POST, request.FILES)
    files = PatientFile.objects.filter(appointment=appointment)

    if form.is_valid():
        form.instance.appointment = appointment
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