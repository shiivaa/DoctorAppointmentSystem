
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from .models import Feedback
from appointment.models import Appointment
from doctor.models import Doctor

from .forms import FeedbackForm
from . import services

#create view for a user has logined 
@login_required
def feedback_create_view(request, appointment_pk):
    
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    patient = getattr(request.user, 'patient', None)

    #if user is not patient raise an error
    if not patient:
        raise PermissionDenied("Only registered patients can submit feedback.")

    #check logic via services.py
    try:
        services.can_patient_submit_feedback(patient=patient, appointment=appointment)
    except PermissionDenied as e:
        messages.error(request, str(e))
        return redirect('appointment:my-appointments')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.appointment = appointment
            feedback.patient = patient
            feedback.doctor = appointment.doctor
            feedback.save()

            messages.success(
                request,
                "Congratulation! Your feedback has been submitted successfully and waiting for confirmation."
            )
            return redirect('appointment:my-appointments')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'feedback/feedback_form.html', context)

#show list of feedbacks registered for a doctor
def doctor_feedback_list_view(request, doctor_pk):
    
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    feedback_list = (Feedback.objects.filter(doctor=doctor, is_confirmed=True).select_related('patient__user').order_by('-created_at'))

    
    paginator = Paginator(feedback_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    average_rating = services.get_doctor_average_rating(doctor)

    context = {
        'doctor': doctor,
        'feedbacks': page_obj,         
        'page_obj': page_obj,          
        'is_paginated': page_obj.has_other_pages(),
        'average_rating': average_rating,
    }
    return render(request, 'feedback/doctor_feedback_list.html', context)