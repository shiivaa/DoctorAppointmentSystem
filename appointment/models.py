from django.db import models

# Create your models here.

class Appointment(models.Model):

    booking_status_choices = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    visit_status_choices = [
        ('visited', 'Visited'),
        ('absent', 'Absent'),
    ]


    patient = models.ForeignKey('user.Patient',on_delete=models.CASCADE,related_name='appointments')

    doctor = models.ForeignKey('doctor.Doctor',on_delete=models.CASCADE,related_name='appointments')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    #transaction = models.OneToOneField('Transaction', on_delete=models.PROTECT,related_name='appointment')
    #deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)

    booking_status = models.CharField(max_length=20,choices=booking_status_choices,default='confirmed')

    visit_status = models.CharField(
        max_length=20,
        choices=visit_status_choices,
        default='absent')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'start_time'],
                name='unique_doctor_appointment_start'
            )
        ]
        

    def __str__(self):
        return f'Appointment {self.doctor} - {self.start_time} - {self.end_time}'



