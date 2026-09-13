from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model

from .models import Doctor, Specialty, WorkingShift

# Register your models here.

User = get_user_model()

class DoctorAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
    )
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=12)
    email = forms.EmailField(required=False)
    gender = forms.ChoiceField(
        choices=User.gender_choices,
        required=False,
    )
    national_code = forms.CharField(max_length=10, required=False)
    birth_date = forms.DateField(required=False)

    class Meta:
        model = Doctor
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'phone',
            'email',
            'gender',
            'national_code',
            'birth_date',
            'specialty',
            'medical_license_number',
            'address',
            'visit_fee',
            'visit_duration',
            'bio',
            'avatar'
        ]

    def save(self, commit=True):
        doctor = super().save(commit=False)

        if doctor.pk:
            user = doctor.user

            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.phone = self.cleaned_data['phone']
            user.email = self.cleaned_data['email']
            user.gender = self.cleaned_data['gender']
            user.national_code = self.cleaned_data['national_code']
            user.birth_date = self.cleaned_data['birth_date']

            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])

            user.save()

        else:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                gender=self.cleaned_data['gender'],
                national_code=self.cleaned_data['national_code'],
                birth_date=self.cleaned_data['birth_date'],
            )

            doctor.user = user

        if commit:
            doctor.save()

        return doctor

class WorkingShiftInline(admin.TabularInline):
    model = WorkingShift
    extra = 1
    fields = ('day_of_week', 'start_time', 'end_time')
    ordering = ('day_of_week', 'start_time')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorAdminForm
    inlines = [WorkingShiftInline]

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}

@admin.register(WorkingShift)
class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ["doctor", "day_of_week", "start_time", "end_time"]