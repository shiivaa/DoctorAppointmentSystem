from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings




# Create your models here.
class Feedback(models.Model):

    class Rate(models.IntegerChoices):
        TERRIBLE=1,_('Extremely Dissatisfied')
        POOR=2,_('Dissatisfied')
        AVERAGE=3,_('Neutral')
        GOOD=4,_('Satisfied')
        EXCELLENT=5,_('Extremely Satisfied')
    patient=models.ForeignKey('user.Patient',on_delete=models.CASCADE,related_name=_("submitted_feedbacks"),verbose_name=_("Patient"))    
    doctor = models.ForeignKey('doctor.Doctor',on_delete=models.CASCADE,related_name=_("received_feedbacks"),verbose_name=_("Doctor") )
    appointment = models.OneToOneField( 'appointment.Appointment', on_delete=models.SET_NULL,null=True, blank=True,related_name=_("Feedback"),verbose_name=_("Appointment") )
    comment=models.TextField(max_length=400,blank=True)
    rate=models.PositiveSmallIntegerField(choices=Rate.choices, default=Rate.AVERAGE, validators=[MinValueValidator(1),MaxValueValidator(5)],help_text=_("Please choose rank between 1 and 5"))
    created_at=models.DateTimeField(auto_now_add=True,verbose_name=_("Created At"))
    updated_at=models.DateTimeField(auto_now=True,verbose_name=_("Updated At"))
    is_confirmed= models.BooleanField(default=False,verbose_name=_('Is Confirmed'),help_text=_('Designates whether this feedback is publicly visible. Staff must approve it.'),)

    def __str__(self):
        return f"Feedback By {self.patient} for {self.doctor}  : rate {self.rate}"

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        ordering = ['-created_at'] 
   
        constraints = [
            models.UniqueConstraint(fields=['patient', 'appointment'], name='unique_feedback_per_appointment')]
