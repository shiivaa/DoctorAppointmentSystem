from django.db.models import Avg
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Feedback
from user.models import Patient
from appointment.models import Appointment


#this function verified the condition for writing a feedback
def can_patient_submit_feedback(patient: Patient, appointment: Appointment):
    
    #check patient who write comment the same as visited patient
    if appointment.patient != patient:
        raise PermissionDenied("You are not allowed to leave feedback for this appointment.")

    #appointment time is passed
    if appointment.start_time >= timezone.now():
        raise PermissionDenied("You can only leave feedback for past appointments.")
    #the first time feedback is registered for this appointment
    if hasattr(appointment, 'feedback'):
        raise PermissionDenied("One feedback has already been submitted for this appointment.")
    
    return True

#this function return average of rates confirmed for this doctor
def get_doctor_average_rating(doctor):
    #calculate average of confirmed rate
    result = Feedback.objects.filter(doctor=doctor, is_confirmed=True).aggregate(average_rating=Avg('rate') )
    value=result.get('average_rating')
    #if there is no confirmed rate return 0
    return round(value, 1) if value is not None else 0.0
