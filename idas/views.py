from django.shortcuts import render, redirect, HttpResponse
from .forms import (
    CustomSignupForm, TimeSlotPresetForm, TimeSlotFormSet,
    TimeSlotForm
)
from django.contrib.auth import login
from .models import Profile, TimeSlotPreset, TimeSlot
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q
from collections import defaultdict
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST


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


@login_required
def booking_view(request):
    # Create a datetime.date object for the target date
    target_date = date(2023, 11, 28)

    # Retrieve all TimeSlotPreset instances that are active on the target date
    active_presets = TimeSlotPreset.objects.filter(
        Q(start_date__lte=target_date, end_date__gte=target_date) |
        Q(start_date=target_date) |
        Q(repeat_days__contains=target_date.strftime('%a'))
    )

    # Retrieve all TimeSlot instances associated with the active presets
    all_time_slots = TimeSlot.objects.filter(preset__in=active_presets)

    # Organize time slots by preset name
    time_slots_by_preset = defaultdict(list)
    for time_slot in all_time_slots:
        time_slots_by_preset[time_slot.preset.name].append(str(time_slot))

    # Convert the defaultdict to a regular dictionary
    time_slots_by_preset = dict(time_slots_by_preset)

    # Pass the time slots as part of the context
    context = {
        'target_date': target_date,
        'time_slots_by_preset': time_slots_by_preset,
    }

    return render(request, 'idas/booking.html', context)


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
            form.instance.preset = preset
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
@require_POST
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
@require_POST
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
