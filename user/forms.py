from django import forms
from django.contrib.auth import get_user_model
from datetime import date
from .models import Patient

import re

User = get_user_model()

def validate_phone(phone):
    if not re.fullmatch(r'98\d{10}', phone):
        raise forms.ValidationError(
            "Phone number must start with 98 and contain exactly 12 digits"
        )

    return phone

class SendOTPForm(forms.Form):
    phone = forms.CharField(
        min_length=12,
        max_length=12
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        return validate_phone(phone)

class VerifyOTPForm(forms.Form):
    code = forms.CharField(
        min_length=6,
        max_length=6,
    )

    def clean_code(self):
        code = self.cleaned_data["code"]

        if not code.isdigit():
            raise forms.ValidationError(
                "Code must contain only digits"
            )
        return code

class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(widget=forms.PasswordInput)

class GoogleRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=30
    )

    first_name = forms.CharField(
        max_length=150
    )

    last_name = forms.CharField(
        max_length=150
    )

    gender = forms.ChoiceField(
        choices=User.gender_choices
    )

    national_code = forms.CharField(
        min_length=10,
        max_length=10
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "User with this username already exists."
            )

        return username

    def clean_national_code(self):
        national_code = self.cleaned_data["national_code"]

        if not national_code.isdigit():
            raise forms.ValidationError(
                "National code must contain only digits"
            )

        if User.objects.filter(national_code=national_code).exists():
            raise forms.ValidationError(
                "This national code already registered."
            )

        return national_code

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]

        if birth_date > date.today():
            raise forms.ValidationError(
                "Birth date cannot be in the future."
            )

class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=30,
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput
    )

    first_name = forms.CharField(
        max_length=150
    )

    last_name = forms.CharField(
        max_length=150
    )

    email = forms.EmailField()

    gender = forms.ChoiceField(
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
        )
    )

    national_code = forms.CharField(
        min_length=10,
        max_length=10,
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "User with this username already exists."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )
        return email

    def clean_national_code(self):
        national_code = self.cleaned_data["national_code"]

        if not national_code.isdigit():
            raise forms.ValidationError(
                "National code must contain only digits"
            )

        if User.objects.filter(national_code=national_code).exists():
            raise forms.ValidationError(
                "This national code already registered."
            )
        return national_code

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]

        if birth_date > date.today():
            raise forms.ValidationError(
                "Birth date cannot be in the future."
            )
        return birth_date

class PatientProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=150
    )
    last_name = forms.CharField(
        max_length=150
    )

    email = forms.EmailField()

    gender = forms.ChoiceField(
        choices=User.gender_choices
    )

    national_code = forms.CharField(
        min_length=10,
        max_length=10,
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    insurance_number = forms.CharField(
        min_length=10,
        max_length=10,
    )

    address = forms.CharField(
        max_length=100,
        widget=forms.TextInput()
    )

    # Store the current user for unique field validation
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

    def clean_email(self):
        email = self.cleaned_data["email"]

        query = User.objects.filter(email=email)

        if self.user:
            query = query.exclude(pk=self.user.pk)

        if query.exists():
            raise forms.ValidationError(
                "This email is already registered."
            )
        return email

    def clean_national_code(self):
        national_code = self.cleaned_data["national_code"]

        if not national_code.isdigit():
            raise forms.ValidationError(
                "National code must contain only digits"
            )

        query = User.objects.filter(national_code=national_code)

        if self.user:
            query = query.exclude(pk=self.user.pk)

        if query.exists():
            raise forms.ValidationError(
                "This national code already registered."
            )
        return national_code

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]

        if birth_date > date.today():
            raise forms.ValidationError(
                "Birth date cannot be in the future."
            )
        return birth_date

    def clean_insurance_number(self):
        insurance_number = self.cleaned_data["insurance_number"]

        if not insurance_number.isdigit():
            raise forms.ValidationError(
                "Insurance number must contain only digits"
            )

        query = Patient.objects.filter(insurance_number=insurance_number)

        if self.user:
            query = query.exclude(user=self.user)

        if query.exists():
            raise forms.ValidationError(
                "This insurance number already exists."
            )
        return insurance_number

    def clean_address(self):
        address = self.cleaned_data["address"].strip()

        if not address:
            raise forms.ValidationError(
                "Address cannot be empty."
            )
        return address