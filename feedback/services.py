from django.db.models import Avg
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Feedback,Patient,Appointment


#this function verified the condition for writing a feedback
def can_patient_submit_feedback(patient: Patient, appointment: Appointment):
    
    #check patient who write comment the same as visited patient
    if appointment.patient != patient:
        raise PermissionDenied("You are not authorized to leave feedback for this appointment.")

    #appointment time is passed
    if appointment.start_time >= timezone.now():
        raise PermissionDenied("You can only leave feedback for past appointments.")
    #the first time feedback is registered for this appointment
    if hasattr(appointment, 'feedback'):
        raise PermissionDenied("Feedback has already been submitted for this appointment.")
    
    return True
git
#this function return average of rates confirmed for this doctor
def get_doctor_average_rating(doctor):
    #calculate average of confirmed rating 
    result = Feedback.objects.filter(
        doctor=doctor, 
        is_confirmed=True
    ).aggregate(
        average_rating=Avg('rating')
    )
    #if there is no confirmed rate return 0
    return result['average_rating'] or 0.0
