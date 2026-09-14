from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'doctor',
        'appointment',
        'rate',
        'is_confirmed',
        'created_at',
    )

    list_filter = (
        'is_confirmed',
        'rate'
    )

    search_fields = (
        'patient__user__username',
        'doctor__user__username',
        'comment'
    )