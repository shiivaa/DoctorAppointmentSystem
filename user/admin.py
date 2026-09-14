from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
    )

    @admin.display(description='Username')
    def username(self, obj):
        return obj.user.username

    @admin.display(description='First name')
    def first_name(self, obj):
        return obj.user.first_name

    @admin.display(description='Last name')
    def last_name(self, obj):
        return obj.user.last_name