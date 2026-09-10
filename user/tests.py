from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .forms import SendOTPForm, VerifyOTPForm, RegistrationForm
from .models import OTP, Patient

User = get_user_model()

class OTPFormTest(TestCase):

    def test_phone(self):
        form = SendOTPForm(data={
            "phone": "989123456789"
        })

        self.assertTrue(form.is_valid())

    def test_code(self):
        form = VerifyOTPForm(data={
            "code": "123456"
        })

        self.assertTrue(form.is_valid())


class RegisterFormTest(TestCase):

    def data(self):
        return {
            "username": "testuser",
            "password": "123456",
            "first_name": "test",
            "last_name": "user",
            "email": "test@test.com",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13)
        }

    def test_register(self):
        form = RegistrationForm(data=self.data())

        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        User.objects.create_user(
            username="testuser",
            password="123456",
            email="one@test.com",
            phone="989123456789",
            gender="male",
            national_code="9876543210",
            birth_date=date(1990, 11, 13)
        )

        form = RegistrationForm(data=self.data())

        self.assertFalse(form.is_valid())

class OTPViewTest(TestCase):

    def test_send_otp(self):
        response = self.client.post(
            reverse("send_otp"),
            {"phone": "989123456789"}
        )

        self.assertRedirects(response, reverse("verify_otp"))
        self.assertEqual(OTP.objects.count(), 1)

    def test_verify_otp(self):
        phone = "989123456789"
        code = "123456"

        session = self.client.session
        session["otp_phone"] = phone
        session["otp_code"] = code
        session.save()

        OTP.objects.create(
            phone=phone,
            code=code,
            expiry_date=timezone.now() + timedelta(minutes=3)
        )

        response = self.client.post(
            reverse("verify_otp"),
            {"code": code}
        )

        self.assertRedirects(
            response,
            reverse("complete_registration")
        )

class RegisterViewTest(TestCase):

    def setUp(self):
        session = self.client.session
        session["otp_verified_phone"] = "989123456789"
        session.save()

    def data(self):
        return {
            "username": "testuser",
            "password": "123456",
            "first_name": "test",
            "last_name": "user",
            "email": "test@test.com",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13)
        }

    def test_register(self):
        response = self.client.post(
            reverse("complete_registration"),
            self.data()
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(User.objects.count(), 1)

    def test_without_phone(self):
        session = self.client.session
        session.pop("otp_verified_phone")
        session.save()

        response = self.client.get(
            reverse("complete_registration")
        )

        self.assertRedirects(response, reverse("send_otp"))

class PatientProfileTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            email="test@tesst.com",
            phone="989123456789",
            gender="male",
            national_code="1234567890",
            birth_date=date(1990, 11, 13)
        )

        self.client.force_login(self.user)

    def test_profile(self):
        response = self.client.get(
            reverse("patient_profile")
        )

        self.assertEqual(response.status_code, 200)

    def test_update_profile(self):
        data = {
            "first_name": "test",
            "last_name": "user",
            "email": "test1@test.com",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13),
            "insurance_number": "1234567890",
            "address": "Iran"
        }

        response = self.client.post(
            reverse("update_patient_profile"),
            data
        )

        self.assertRedirects(response, reverse("patient_profile"))

    def test_without_login(self):
        self.client.logout()

        response =  self.client.get(
            reverse("patient_profile")
        )

        self.assertRedirects(response, reverse("send_otp"))

class WalletTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            email="test@test.com",
            phone="989123456789",
            gender="male",
            national_code="1234567890",
            birth_date=date(1990, 11, 13)
        )

        self.patient = Patient.objects.create(
            user=self.user,
            insurance_number="1234567890",
            address="Iran"
        )

        self.client.force_login(self.user)

    def test_wallet(self):
        response = self.client.get(
            reverse("wallet")
        )

        self.assertEqual(response.status_code, 200)

    def test_transactions(self):
        response = self.client.get(
            reverse("wallet_transactions")
        )
        self.assertEqual(response.status_code, 200)

class LogoutTest(TestCase):

    def test_logout(self):
        user = User.objects.create_user(
            username="testuser",
            password="123456",
            email="test@test.com",
            phone="989123456789",
            gender="male",
            national_code="1234567890",
            birth_date=date(1990, 11, 13)
        )

        self.client.force_login(user)

        response = self.client.post(
            reverse("logout")
        )

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)