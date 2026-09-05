from django.db import models
from django.contrib.auth.models import AbstractUser
from Appointment.models import *

# Create your models here.
class OTP(models.Model):
    phone = models.CharField(max_length=12)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

class User(AbstractUser):
    gender_choices = (
        ('male', 'male'),
        ('female', 'female'),
    )
    gender = models.CharField(max_length=10, choices=gender_choices, default='male')
    national_code = models.CharField(max_length=10, unique=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=12, unique=True)
    medical_license_number = models.CharField(max_length=6, unique=True, blank=True, null=True)

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    insurance_number = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=100)

class Wallet(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    type_choices = (
        ("deposit", "deposit"),
        ("payment", "payment"),
        ("refund", "refund")
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    appointment = models.OneToOneField("Appointment",
            on_delete=models.CASCADE, related_name='transaction', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=type_choices, default='deposit')
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)