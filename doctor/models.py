from django.core.exceptions import ValidationError
from django.db import models


class Specialty(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="specialty title")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Doctor(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    medical_license_number = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True)
    visit_fee = models.DecimalField(max_digits=9, decimal_places=0, default=0)
    visit_duration = models.PositiveIntegerField(
        default=30, help_text="duration of each visit in minutes(like: 20, 30, 60)"
    )
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Dr. {full_name}" if full_name else f"Dr. {self.user.username}"

class WorkingShift(models.Model):
    class Weekday(models.IntegerChoices):
        SATURDAY = 0, 'SATURDAY'
        SUNDAY = 1, 'SUNDAY'
        MONDAY = 2, 'MONDAY'
        TUESDAY = 3, 'TUESDAY'
        WEDNESDAY = 4, 'WEDNESDAY'
        THURSDAY = 5, 'THURSDAY'
        FRIDAY = 6, 'FRIDAY'

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="shifts")
    day_of_week = models.IntegerField(choices=Weekday.choices, verbose_name="Weekday")
    start_time = models.TimeField(verbose_name="Start time")
    end_time = models.TimeField(verbose_name="End time")

    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name = "Working shift"
        verbose_name_plural = "Working shifts"

    def clean(self):
        super().clean()

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({"end_time": "End time must be after start time."})

        overlapping_shifts = WorkingShift.objects.filter(
            doctor=self.doctor,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            overlapping_shifts = overlapping_shifts.exclude(pk=self.pk)

        if overlapping_shifts.exists():
            raise ValidationError("This time overlaps with the others.")

        if hasattr(self, "doctor") and self.doctor and self.doctor.visit_duration:
            total_minutes = (
                (self.end_time.hour * 60 + self.end_time.minute) - (self.start_time.hour * 60 + self.start_time.minute)
            )

            if total_minutes < self.doctor.visit_duration:
                raise ValidationError(f"Duration cannot be less than {self.doctor.visit_duration} minutes")



