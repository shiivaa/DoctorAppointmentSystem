from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .forms import (
    SendOTPForm,
    VerifyOTPForm,
    RegistrationForm,
    PatientProfileForm,
    GoogleRegistrationForm,
)
from .models import OTP, Patient, Wallet, Transaction


User = get_user_model()


class OTPFormTest(TestCase):

    def test_phone(self):
        form = SendOTPForm(data={
            "phone": "989123456789"
        })

        self.assertTrue(form.is_valid())

    def test_invalid_phone(self):
        form = SendOTPForm(data={
            "phone": "091234567890"
        })

        self.assertFalse(form.is_valid())

    def test_code(self):
        form = VerifyOTPForm(data={
            "code": "123456"
        })

        self.assertTrue(form.is_valid())

    def test_invalid_code(self):
        form = VerifyOTPForm(data={
            "code": "abc123"
        })

        self.assertFalse(form.is_valid())


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

    def test_duplicate_email(self):
        User.objects.create_user(
            username="otheruser",
            password="123456",
            email="test@test.com",
            phone="989123456788",
            gender="male",
            national_code="9876543210",
            birth_date=date(1990, 11, 13)
        )

        form = RegistrationForm(data=self.data())

        self.assertFalse(form.is_valid())

    def test_invalid_national_code(self):
        data = self.data()
        data["national_code"] = "abc123456a"

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())

    def test_future_birth_date(self):
        data = self.data()
        data["birth_date"] = date.today() + timedelta(days=1)

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())


class PatientProfileFormTest(TestCase):

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

    def data(self):
        return {
            "first_name": "test",
            "last_name": "user",
            "email": "test@test.com",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13),
            "insurance_number": "1234567890",
            "address": "Iran"
        }

    def test_valid_profile(self):
        form = PatientProfileForm(
            data=self.data(),
            user=self.user
        )

        self.assertTrue(form.is_valid())

    def test_empty_address(self):
        data = self.data()
        data["address"] = ""

        form = PatientProfileForm(
            data=data,
            user=self.user
        )

        self.assertFalse(form.is_valid())


class GoogleRegistrationFormTest(TestCase):

    def test_valid_form(self):
        form = GoogleRegistrationForm(data={
            "username": "googleuser",
            "first_name": "google",
            "last_name": "user",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13),
        })

        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        User.objects.create_user(
            username="googleuser",
            password="123456",
            email="one@test.com",
            phone="989123456789",
            national_code="9876543210"
        )

        form = GoogleRegistrationForm(data={
            "username": "googleuser",
            "first_name": "Google",
            "last_name": "User",
            "gender": "male",
            "national_code": "1234567890",
            "birth_date": date(1990, 11, 13)
        })

        self.assertFalse(form.is_valid())


class OTPModelTest(TestCase):

    def test_create_otp(self):
        otp = OTP.objects.create(
            phone="989123456789",
            code="123456",
            expiry_date=timezone.now() + timedelta(minutes=3)
        )

        self.assertEqual(OTP.objects.count(), 1)
        self.assertEqual(str(otp), "989123456789 - 123456")


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890"
        )

        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("123456"))

    def test_user_default_gender(self):
        user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890"
        )

        self.assertEqual(user.gender, "male")


class PatientModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890"
        )

    def test_create_patient(self):
        patient = Patient.objects.create(
            user=self.user,
            insurance_number="1111111111",
            address="Iran"
        )

        self.assertEqual(patient.user, self.user)
        self.assertEqual(patient.insurance_number, "1111111111")

    def test_patient_str(self):
        self.user.first_name = "test"
        self.user.last_name = "user"
        self.user.save()

        patient = Patient.objects.create(
            user=self.user,
            insurance_number="1111111111",
            address="Iran"
        )

        self.assertEqual(str(patient), "test user")


class WalletModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890"
        )

        self.patient = Patient.objects.create(
            user=self.user,
            insurance_number="1111111111",
            address="Iran"
        )

    def test_create_wallet(self):
        wallet = Wallet.objects.create(
            patient=self.patient,
        )

        self.assertEqual(wallet.balance, Decimal("0"))

    def test_wallet_str(self):
        wallet = Wallet.objects.create(
            patient=self.patient,
        )

        self.assertEqual(str(wallet), "testuser - 0")


class TransactionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890"
        )

        self.patient = Patient.objects.create(
            user=self.user,
            insurance_number="1111111111",
            address="Iran"
        )

        self.wallet = Wallet.objects.create(
            patient=self.patient
        )

    def test_create_transaction(self):
        transaction = Transaction.objects.create(
            wallet=self.wallet,
            amount=Decimal("50000"),
            type="deposit",
            description="Wallet Charge"
        )

        self.assertEqual(transaction.amount, Decimal("50000"))
        self.assertEqual(transaction.type, "deposit")
        self.assertEqual(self.wallet.transactions.count(), 1)


class OTPViewTest(TestCase):

    def test_send_otp(self):
        response = self.client.post(
            reverse("send_otp"),
            {"phone": "989123456789"}
        )

        self.assertRedirects(response, reverse("verify_otp"))
        self.assertEqual(OTP.objects.count(), 1)

    def test_send_otp_invalid_phone(self):
        response = self.client.post(
            reverse("send_otp"),
            {"phone": "12345"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(OTP.objects.count(), 0)

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

    def test_verify_wrong_otp(self):
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
            {"code": "999999"}
        )

        self.assertEqual(response.status_code, 200)

    def test_expired_otp(self):
        phone = "989123456789"
        code = "123456"

        session = self.client.session
        session["otp_phone"] = phone
        session["otp_code"] = code
        session.save()

        OTP.objects.create(
            phone=phone,
            code=code,
            expiry_date=timezone.now() - timedelta(minutes=1)
        )

        response = self.client.post(
            reverse("verify_otp"),
            {"code": code}
        )

        self.assertEqual(response.status_code, 200)


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


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            phone="989123456789",
            email="test@test.com",
            national_code="1234567890",
        )

    def test_login(self):
        response = self.client.post(
            reverse("login_user"),
            {
                "username": "testuser",
                "password": "123456"
            }
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_wrong_password(self):
        response = self.client.post(
            reverse("login_user"),
            {
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class PatientProfileTest(TestCase):

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

        response = self.client.get(
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

    def test_wallet_charge(self):
        response = self.client.post(
            reverse("wallet"),
            {"amount": "50000"}
        )

        self.assertRedirects(response, reverse("wallet"))

        wallet = Wallet.objects.get(patient=self.patient)

        self.assertEqual(wallet.balance, Decimal("50000"))
        self.assertEqual(wallet.transactions.count(), 1)

    def test_invalid_amount(self):
        response = self.client.post(
            reverse("wallet"),
            {"amount": "-100"}
        )

        self.assertRedirects(response, reverse("wallet"))

        wallet = Wallet.objects.get(patient=self.patient)

        self.assertEqual(wallet.balance, Decimal("0"))


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