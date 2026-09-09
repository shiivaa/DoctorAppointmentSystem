from django.contrib import admin
from .models import Doctor, WorkingShift

class WorkingShiftInline(admin.TabularInline):
    model = WorkingShift
    extra = 1
    fields = ('day_of_week', 'start_time', 'end_time')
    ordering = ('day_of_week', 'start_time')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot_duration')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    inlines = [WorkingShiftInline]

@admin.register(WorkingShift)
class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'doctor')
    ordering = ('doctor', 'day_of_week', 'start_time')


#--------------------------------------------------------------------------
#--------------------------------models.py---------------------------------
#--------------------------------------------------------------------------


from django.core.exceptions import ValidationError
from django.db import models


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

