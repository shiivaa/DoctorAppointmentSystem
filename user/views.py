from decimal import Decimal

from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model, login, logout, authenticate
from datetime import timedelta
from .models import OTP, Patient, Wallet, Transaction
from .forms import SendOTPForm, VerifyOTPForm, RegistrationForm, PatientProfileForm, LoginForm
from django.db.models import Count, Avg
from doctor.models import Doctor

import random


User = get_user_model()

def sign_in(request):
    return render(request, "user/sing_in.html")

def send_otp(request):
    if request.method == "GET":
        form = SendOTPForm()

        return render(request, "user/send_otp.html", {
            "form": form
            }
        )

    form = SendOTPForm(request.POST)

    if not form.is_valid():
        return render(request, "user/send_otp.html", {
            "form": form
            }
        )

    phone = form.cleaned_data["phone"]

    code = str(random.randint(100000, 999999))

    OTP.objects.create(
        phone=phone,
        code=code,
        expiry_date=timezone.now() + timedelta(minutes=3)
    )

    request.session["otp_phone"] = phone
    request.session["otp_code"] = code # Just for show in template

    return redirect("verify_otp")

def verify_otp(request):
    phone = request.session.get("otp_phone")

    if not phone:
        return redirect("send_otp")

    if request.method == "GET":
        form = VerifyOTPForm()

        return render(request, "user/verify_otp.html",{
            "form": form,
            "phone":phone,
            "code":request.session["otp_code"]
            }
        )

    form = VerifyOTPForm(request.POST)

    if not form.is_valid():
        return render(request, "user/verify_otp.html", {
            "form": form,
            "phone":phone,
            "code": request.session["otp_code"]
            }
        )

    code = form.cleaned_data["code"]

    try:
        otp = OTP.objects.get(phone=phone, code=code)

    except OTP.DoesNotExist:
        form.add_error("code", "Your code is invalid.")

        return render(request, "user/verify_otp.html", {
            "form": form,
            "phone":phone,
            "code":request.session["otp_code"]
            }
        )

    if otp.expiry_date < timezone.now():
        form.add_error("code", "Your code is expired")

        return render(request, "user/verify_otp.html", {
            "form": form,
            "phone":phone,
            "code": request.session["otp_code"]
            }
        )

    try:
        user = User.objects.get(phone=phone)

    except User.DoesNotExist:
        request.session["otp_verified_phone"] = phone

        del request.session["otp_code"]
        del request.session["otp_phone"]

        return redirect("complete_registration")

    login(request, user)

    del request.session["otp_phone"]
    del request.session["otp_code"]

    return redirect("home")

def login_user(request):
    if request.method == "GET":
        form = LoginForm()

        return render(request, "user/login.html", {
            "form": form
        })

    form = LoginForm(request.POST)

    if not form.is_valid():
        return render(request, "user/login.html",{
            "form": form
        })

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        form.add_error(None, "Username or password is incorrect.")

        return render(request, "user/login.html",{
            "form": form,
        })

    login(request, user)

    return redirect("home")

def complete_registration(request):
    phone = request.session.get("otp_verified_phone")

    if not phone:
        return redirect("send_otp")

    if request.method == "GET":
        form = RegistrationForm()

        return render(request, "user/complete_registration.html", {
            "form": form,
            }
        )

    form = RegistrationForm(request.POST)

    if not form.is_valid():
        return render(request, "user/complete_registration.html", {
            "form": form,
            }
        )

    if User.objects.filter(phone=phone).exists():
        form.add_error(
            None,
            "User with this phone number already exists."
        )

        return render(request, "user/complete_registration.html", {
            "form": form
            }
        )

    user = User.objects.create_user(
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
        email=form.cleaned_data["email"],
        phone=phone,
        gender=form.cleaned_data["gender"],
        national_code = form.cleaned_data["national_code"],
        birth_date = form.cleaned_data["birth_date"],
    )

    del request.session["otp_verified_phone"]

    login(request, user)

    return redirect("home")

def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

    return render(request, "user/home.html")

def patient_profile(request):
    if not request.user.is_authenticated:
        return redirect("send_otp")

    try:
        patient = request.user.patient

    except Patient.DoesNotExist:
        patient = None

    return render(request, "user/patient_profile.html",{
        "user": request.user,
        "patient": patient
        }
    )

def update_patient_profile(request):
    if not request.user.is_authenticated:
        return redirect("send_otp")

    try:
        patient = request.user.patient

    except Patient.DoesNotExist:
        patient = None

    if request.method == "GET":
        initial_data = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "gender": request.user.gender,
            "national_code": request.user.national_code,
            "birth_date": request.user.birth_date
        }

        if patient:
            initial_data.update({
                "insurance_number": patient.insurance_number,
                "address": patient.address,
            })

        form = PatientProfileForm(
            initial=initial_data,
            user=request.user
        )

        return render(request, "user/update_patient_profile.html",{
            "form": form
            }
        )

    form = PatientProfileForm(
        request.POST,
        user=request.user,
    )

    if not form.is_valid():
        return render(request, "user/update_patient_profile.html", {
            "form": form
            }
        )

    request.user.first_name = form.cleaned_data["first_name"]
    request.user.last_name = form.cleaned_data["last_name"]
    request.user.email = form.cleaned_data["email"]
    request.user.gender = form.cleaned_data["gender"]
    request.user.national_code = form.cleaned_data["national_code"]
    request.user.birth_date = form.cleaned_data["birth_date"]

    request.user.save()

    if patient:
        patient.insurance_number = form.cleaned_data["insurance_number"]
        patient.address = form.cleaned_data["address"]
        patient.save()

    else:
        patient = Patient.objects.create(
            user=request.user,
            insurance_number=form.cleaned_data["insurance_number"],
            address=form.cleaned_data["address"],
        )

    Wallet.objects.get_or_create(
        patient=patient
    )

    return redirect("patient_profile")

def wallet(request):
    if not request.user.is_authenticated:
        return redirect("send_otp")

    try:
        patient = request.user.patient

    except Patient.DoesNotExist:
        return redirect("update_patient_profile")

    wallet, created = Wallet.objects.get_or_create(
        patient=patient
    )

    if request.method == "POST":
        amount = int(request.POST["amount"])

        if amount:
            wallet.balance += Decimal(amount)
            wallet.save()

            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                type="deposit",
                description="Wallet Charge"
            )

        return redirect("wallet")

    return render(request, "user/wallet.html",{
        "wallet": wallet
        }
    )

def transactions(request):
    if not request.user.is_authenticated:
        return redirect("send_otp")

    try:
        patient = request.user.patient

    except Patient.DoesNotExist:
        return redirect("update_patient_profile")

    wallet, created = Wallet.objects.get_or_create(
        patient=patient
    )

    transactions = wallet.transactions.all()

    return render(request, "user/transactions.html",{
        "transactions": transactions
        }
    )

def home(request):
    doctors = (
        Doctor.objects.select_related("user", "specialty")
        .annotate(
            avg_rating=Avg("received_feedbacks__rate"),
            feedbacks_count=Count("received_feedbacks"),
        )
    )
    return render(request, "user/home.html", {'doctors': doctors})