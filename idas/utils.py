from .models import TimeSlotPreset, TimeSlot, Appointment
from django.db.models import Q
from collections import defaultdict


def is_slot_taken(app_date, slot):
    date_appointment = Appointment.objects.filter(appointment_date=app_date, appointment_slot=slot)
    return date_appointment.exists()


def get_slots_by_date(target_date, by_preset=False):
    active_presets = TimeSlotPreset.objects.filter(
        Q(start_date__lte=target_date, end_date__gte=target_date) |
        Q(start_date=target_date) |
        Q(repeat_days__contains=target_date.strftime('%a'))
    )

    all_time_slots = TimeSlot.objects.filter(preset__in=active_presets)
    all_time_slots_with_is_taken = []

    for slot in all_time_slots:
        all_time_slots_with_is_taken.append({
            'is_taken': is_slot_taken(target_date, slot),
            'slot': slot
        })

    if by_preset:
        time_slots_by_preset = defaultdict(list)
        for item in all_time_slots_with_is_taken:
            time_slots_by_preset[item['slot'].preset.name].append(item)

        return dict(time_slots_by_preset)

    else:
        return all_time_slots
