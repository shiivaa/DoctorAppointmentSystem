from datetime import timedelta, datetime

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from doctor.models import Doctor, WorkingShift
from user.models import Wallet, Transaction
from feedback.models import Feedback
from .models import Appointment

from .services import get_doctor_slots

from django.core.mail import send_mail


# create weekdays schedule for doctor - user can select one
def doctor_working_days(request, doctor_pk):

    doctor = get_object_or_404(Doctor.objects.select_related('user'),pk=doctor_pk)

    today = timezone.localdate()

    days = []

    working_days = set(
        WorkingShift.objects.filter(doctor=doctor).values_list('day_of_week', flat=True))

    for i in range(30):

        current_date = today + timedelta(days=i)

        weekday = (current_date.weekday() + 2) % 7

        days.append({
            'date': current_date,
            'is_working_day': weekday in working_days,
        })

    return render(request,'appointment/working_days.html',{
            'doctor': doctor,
            'days': days,
    })



# create working day time slots for each day user wants to select
def doctor_appointment_times(request, doctor_pk, date):

    doctor = get_object_or_404(Doctor.objects.select_related('user'),pk=doctor_pk)

    try:
        selected_date = datetime.strptime(date,'%Y-%m-%d').date()

    except ValueError:
        messages.error(request,'Invalid date.')

        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor.pk)

    # Make sure selected date is not in the past
    if selected_date < timezone.localdate():

        messages.error(request,'You cannot view appointments for a past date.')

        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor.pk)

    slots = get_doctor_slots(doctor=doctor,selected_date=selected_date)

    return render(
        request,
        'appointment/appointment_times.html',
        {
            'doctor': doctor,
            'selected_date': selected_date,
            'slots': slots,
        }
    )

# create appointment for in system for user and doctor

@login_required
def book_appointment(request, doctor_pk):

    if request.method != 'POST':
        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor_pk)

    doctor = get_object_or_404(Doctor.objects.select_related('user'),pk=doctor_pk)

    # Get current patient
    patient = getattr(request.user,'patient',None)

    if patient is None:
        messages.error(request,
            'Complete your profile information for booking a visit time .'
        )
        return redirect('update_patient_profile')

    # Get selected appointment start time from request
    start_time_string = request.POST.get('start_time')

    if not start_time_string:

        messages.error(request,'Please select an appointment time.')

        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor.pk)

    try:

        # Convert selected start time string to datetime
        start_time = datetime.fromisoformat(start_time_string)

        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time)

    except ValueError:
        messages.error(request,'Invalid appointment time.')

        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor.pk)

    end_time = start_time + timedelta(minutes=doctor.visit_duration)

    weekday = (start_time.date().weekday() + 2) % 7

    valid_shift = WorkingShift.objects.filter(
        doctor=doctor,
        day_of_week=weekday,
        start_time__lte=start_time.time(),
        end_time__gte=end_time.time()
    ).exists()

    if not valid_shift:

        messages.error(request,'This time is not a valid working time for the doctor.')

        return redirect(
            'appointment:doctor-appointment-times',
            doctor_pk=doctor.pk,
            date=start_time.date().strftime('%Y-%m-%d')
        )

    # Make sure selected appointment is not in the past
    if start_time <= timezone.now():

        messages.error(request,'You cannot book a past appointment.')

        return redirect(
            'appointment:doctor-appointment-times',
            doctor_pk=doctor.pk,
            date=start_time.date().strftime('%Y-%m-%d')
        )

    # Start atomic transaction for booking and payment
    try:
        with transaction.atomic():

            # Lock patient's wallet during booking process
            wallet = Wallet.objects.select_for_update().get(patient=patient)

            if wallet.balance < doctor.visit_fee:

                messages.error(request,'Your wallet balance is not enough.')

                return redirect(
                    'appointment:doctor-appointment-times',
                    doctor_pk=doctor.pk,
                    date=start_time.date().strftime('%Y-%m-%d')
                )

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                start_time=start_time,
                end_time=end_time,
                booking_status='confirmed',
                visit_status='absent',
            )

            wallet.balance -= doctor.visit_fee

            wallet.save(update_fields=['balance'])

            Transaction.objects.create(
                wallet=wallet,
                appointment=appointment,
                amount=doctor.visit_fee,
                type='payment',
                description=(
                    f'Appointment payment for {doctor}'
                )
            )

    except Wallet.DoesNotExist:

        messages.error(request,'Your wallet was not found.')

        return redirect('appointment:doctor-appointment-days',doctor_pk=doctor.pk)

    # Handle booking of the same appointment by two different patientsa
    except IntegrityError:

        messages.error(request,'This appointment was just booked by another user.')

        return redirect(
            'appointment:doctor-appointment-times',
            doctor_pk=doctor.pk,
            date=start_time.date().strftime('%Y-%m-%d')
        )

    send_mail(
        subject="Appointment Confirmation",
        message=f'''
    Your appointment has been confirmed.

    Doctor: Dr. {doctor.user.first_name} {doctor.user.last_name}
    Date: {appointment.start_time.date()}
    Time: {appointment.start_time.strftime('%H:%M')}
    Visit fee: {appointment.doctor.visit_fee}
    ''',
        from_email=None,
        recipient_list=[appointment.patient.user.email],
    )

    messages.success(request,'Your appointment was booked successfully.')

    return render(request,'appointment/booking_success.html',
        {
            'appointment': appointment,
        }
    )


@login_required
def my_appointments(request):

    # Get current patient

    patient = getattr(request.user,'patient',None)

    if patient is None:
        messages.error(request,
            'Complete your profile information please! then you see your appointments.'
        )
        return redirect('update_patient_profile')

    # Get patient's appointments

    appointments = (
        Appointment.objects
        .filter(patient=patient)
        .select_related(
            'doctor',
            'doctor__user'
        )
        .order_by('-start_time')
    )

    # Get feedbacks already submitted

    feedbacks = Feedback.objects.filter(appointment__in=appointments)

    feedback_by_appointment = {
        feedback.appointment_id: feedback
        for feedback in feedbacks
    }

    # Prepare appointments for template

    appointment_list = []

    for appointment in appointments:

        feedback = feedback_by_appointment.get(appointment.pk)

        appointment_list.append({
            'appointment': appointment,

            'is_visited': (appointment.visit_status == 'visited'),

            'has_feedback': feedback is not None,

            'feedback': feedback,

            'can_submit_feedback': (
                appointment.visit_status == 'visited'
                and feedback is None
                and appointment.booking_status == 'confirmed'
            ),
        })

    # Separate upcoming and past appointments

    upcoming_appointments = [
        item
        for item in appointment_list
        if not item['is_visited']
    ]

    past_appointments = [
        item
        for item in appointment_list
        if item['is_visited']
    ]

    return render(
        request,
        'appointment/my_appointments.html',
        {
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
        }
    )