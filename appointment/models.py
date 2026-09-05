from django.db import models
from user.models import  Patient , Transaction
# Create your models here.

class Appointment(models.Model):

    booking_status_choices = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    visit_status_choices = [
        ('visited', 'Visited'),
        ('absent', 'Absent'),
    ]


    patient = models.ForeignKey('Patient',on_delete=models.CASCADE,related_name='appointments')

    timeslot = models.OneToOneField('TimeSlot',on_delete=models.PROTECT,related_name='appointment') #TS

    # we can find doctor info from time slot

    #transaction = models.OneToOneField('Transaction', on_delete=models.PROTECT,related_name='appointment')
    #deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)

    booking_status = models.CharField(max_length=20,choices=booking_status_choices,default='confirmed')

    visit_status = models.CharField(
        max_length=20,
        choices=visit_status_choices,
        default='absent')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



