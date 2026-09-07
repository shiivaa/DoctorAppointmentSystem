
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied


from .models import Feedback
from appointment.models import Appointment
from doctor.models import Doctor


from .forms import FeedbackForm
from . import services

#this class responsible for creating a feedback in database
class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'feedback/feedback_form.html' 

    def dispatch(self, request, *args, **kwargs):
       
        self.appointment = get_object_or_404(Appointment, pk=self.kwargs['appointment_pk'])
        self.patient = getattr(request.user, 'patient', None)

        if not self.patient:
            raise PermissionDenied("Only registered patients can submit feedback.")

        try:
            services.can_patient_submit_feedback(patient=self.patient, appointment=self.appointment)
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('appointments:my_appointments')

        return super().dispatch(request, *args, **kwargs)
    
    #sending info of appointment to show
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = get_object_or_404(Appointment, pk=self.kwargs['appointment_pk'])
        return context

    def form_valid(self, form):
    
        appointment = get_object_or_404(Appointment, pk=self.kwargs['appointment_pk'])
        patient = getattr(self.request.user, 'patient', None)
        if not patient:
            raise PermissionDenied("Only patients can submit feedback.")
        try:
            services.can_patient_submit_feedback(patient=patient, appointment=appointment)
        except PermissionDenied as e:
            messages.error(self.request, str(e))
            return redirect('some-error-page-or-dashboard') 


        form.instance.appointment = appointment
        form.instance.patient = patient
        form.instance.doctor = appointment.doctor
        

        messages.success(self.request, "Congrat! Your feedback has been submitted successfully and waiting for confirmation.")
        
        return super().form_valid(form)
        
    def get_success_url(self):
        
        return reverse_lazy('appointments:my_appointments')


#show list of feedbacks
class DoctorFeedbackListView(ListView):
    model = Feedback
    template_name = 'feedback/doctor_feedback_list.html'
    context_object_name = 'feedbacks'
    paginate_by = 10
    def get_queryset(self):
       
        self.doctor = get_object_or_404(Doctor, pk=self.kwargs['doctor_pk'])
        queryset = Feedback.objects.filter(doctor=self.doctor,is_confirmed=True).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context['doctor'] = self.doctor
        context['average_rating'] = services.get_doctor_average_rating(self.doctor)
        return context

