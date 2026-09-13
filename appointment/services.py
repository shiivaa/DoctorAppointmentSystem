from datetime import datetime, timedelta

from django.utils import timezone

from .models import Appointment


def get_doctor_slots(doctor, selected_date):

    weekday = (selected_date.weekday() + 2) % 7

    shifts = doctor.shifts.filter(day_of_week=weekday).order_by('start_time')


    day_start = timezone.make_aware(
        datetime.combine(selected_date,datetime.min.time())
    )

    day_end = day_start + timedelta(days=1)

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            start_time__gte=day_start,
            start_time__lt=day_end,
            booking_status='confirmed'
        ).values_list('start_time',flat=True)
    )

    slots = []

    for shift in shifts:
        current_time = datetime.combine(selected_date, shift.start_time)

        while True:

            slot_start = current_time

            slot_end = slot_start + timedelta(minutes=doctor.visit_duration)

            shift_end = datetime.combine(selected_date,shift.end_time)

            if slot_end > shift_end:
                break

            slot_start = timezone.make_aware(slot_start)

            slot_end = timezone.make_aware(slot_end)

            is_booked = slot_start in booked_times
            is_past = slot_start <= timezone.now()

            slots.append({
                'start': slot_start,
                'end': slot_end,
                'is_booked': is_booked,
                'is_past': is_past,
                'is_available': (not is_booked and not is_past),
            })

            current_time += timedelta(minutes=doctor.visit_duration)

    return slots