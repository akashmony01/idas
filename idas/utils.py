from .models import TimeSlotPreset, TimeSlot, Appointment, DayOff
from django.db.models import Q
from collections import defaultdict
from datetime import date


def is_superuser(user):
    return user.is_superuser

def is_staff(user):
    return user.is_authenticated and user.is_staff


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


def is_day_off(input_date):
    active_day_offs = DayOff.objects.filter(
        Q(end_date__gte=date.today()) | Q(end_date__isnull=True),
        start_date__gte=date.today()
    )

    for day_off in active_day_offs:
        if input_date == day_off.start_date:
            return True
        if input_date > day_off.start_date:
            if day_off.end_date:
                if input_date <= day_off.end_date:
                    return True

    return False