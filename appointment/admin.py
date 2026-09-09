from django.contrib import admin

from appointment.models import Appointment
from doctor.models import Doctor, WorkingShift

# Register your models here.

admin.site.register(Appointment)

class WorkingShiftInline(admin.TabularInline):
    model = WorkingShift
    extra = 1
    fields = ('day_of_week', 'start_time', 'end_time')
    ordering = ('day_of_week', 'start_time')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'visit_duration')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    inlines = [WorkingShiftInline]

@admin.register(WorkingShift)
class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'doctor')
    ordering = ('doctor', 'day_of_week', 'start_time')
