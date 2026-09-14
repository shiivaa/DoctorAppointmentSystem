
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointment.models import Appointment
from appointment.services import get_doctor_slots
from doctor.models import Doctor, Specialty, WorkingShift
from feedback.models import Feedback
from user.models import Patient, Wallet, Transaction


User = get_user_model()


class AppointmentViewTestBase(TestCase):

    def setUp(self):

        self.specialty = Specialty.objects.create(title="Cardiology",slug="cardiology",)


        self.patient_user = User.objects.create_user(
            username="patient_test",
            password="TestPassword123!",
            first_name="Ali",
            last_name="Ahmadi",
            gender="male",
            national_code="1234567890",
            birth_date=datetime(2000, 5, 15).date(),
            phone="09120000001",
            email="patient@test.com",
        )

        self.patient = Patient.objects.create(
            user=self.patient_user,
            insurance_number="INS0000001",
            address="Tehran, ValiAsr Street",
        )

        self.wallet = Wallet.objects.create(
            patient=self.patient,
            balance=Decimal("1000.00"),
        )

        self.doctor_user = User.objects.create_user(
            username="doctor_test",
            password="DoctorPassword123!",
            first_name="Reza",
            last_name="Ahmadi",
            gender="male",
            national_code="1234567891",
            birth_date=datetime(1985, 8, 20).date(),
            phone="09120000002",
            email="doctor@test.com",
        )

        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty=self.specialty,
            medical_license_number="1234567890",
            address="Tehran, Keshavarz Boulevard",
            visit_fee=Decimal("250.00"),
            visit_duration=30,
            bio="Experienced cardiologist with more than 10 years of practice.",
        )

        self.future_date = timezone.localdate() + timedelta(days=1)

        self.future_weekday = (self.future_date.weekday() + 2) % 7

        self.shift = WorkingShift.objects.create(
            doctor=self.doctor,
            day_of_week=self.future_weekday,
            start_time=datetime.strptime("09:00","%H:%M",).time(),
            end_time=datetime.strptime("13:00","%H:%M",).time(),
        )

        self.future_start = timezone.make_aware(
            datetime.combine(
                self.future_date,
                datetime.strptime("10:00","%H:%M",).time(),
            )
        )

    def login_patient(self):
        self.client.force_login(self.patient_user)


class AppointmentTests(AppointmentViewTestBase):

    # DOCTOR WORKING DAYS

    def test_doctor_working_days_returns_30_days(self):
        url = reverse(
            "appointment:doctor-appointment-days",
            kwargs={"doctor_pk": self.doctor.pk,},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code,200,)

        self.assertTemplateUsed(response,"appointment/working_days.html",)

        days = response.context["days"]

        self.assertEqual(len(days),30,)

        # Tomorrow is configured as a working day
        self.assertEqual(days[1]["date"],self.future_date,)

        self.assertTrue(days[1]["is_working_day"],)

    # INVALID DATE

    def test_doctor_appointment_times_invalid_date_redirects(self):
        url = reverse(
            "appointment:doctor-appointment-times",
            kwargs={
                "doctor_pk": self.doctor.pk,
                "date": "invalid-date",
            },
        )

        response = self.client.get(url)

        expected_url = reverse(
            "appointment:doctor-appointment-days",
            kwargs={"doctor_pk": self.doctor.pk,},
        )

        self.assertRedirects(response,expected_url,)

        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages),1,)

        self.assertEqual(str(messages[0]),"Invalid date.")

    #  PAST DATE

    def test_doctor_appointment_times_past_date_redirects(self):
        past_date = timezone.localdate() - timedelta(days=1)

        url = reverse(
            "appointment:doctor-appointment-times",
            kwargs={
                "doctor_pk": self.doctor.pk,
                "date": past_date.strftime("%Y-%m-%d")}
        )

        response = self.client.get(url)

        expected_url = reverse(
            "appointment:doctor-appointment-days",
            kwargs={"doctor_pk": self.doctor.pk,},
        )

        self.assertRedirects(response,expected_url,)

        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages),1,)

        self.assertEqual(str(messages[0]),"You cannot view appointments for a past date.",)

    # SERVICE GENERATES SLOTS

    def test_get_doctor_slots_generates_correct_slots(self):
        slots = get_doctor_slots(
            doctor=self.doctor,
            selected_date=self.future_date,)

        self.assertEqual(len(slots),8,)

        first_slot = slots[0]

        self.assertEqual(first_slot["start"].time().strftime("%H:%M"),"09:00")

        self.assertEqual(first_slot["end"].time().strftime("%H:%M"),"09:30")

        self.assertFalse(first_slot["is_booked"])

        self.assertFalse(first_slot["is_past"])

        self.assertTrue(first_slot["is_available"])

    # SERVICE MARKS BOOKED SLOT

    def test_get_doctor_slots_marks_booked_slot(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            start_time=self.future_start,
            end_time=self.future_start + timedelta(minutes=30),
            booking_status="confirmed",
            visit_status="absent",
        )

        slots = get_doctor_slots(doctor=self.doctor,selected_date=self.future_date)

        booked_slot = next(
            slot
            for slot in slots
            if slot["start"] == self.future_start
        )

        self.assertTrue(booked_slot["is_booked"])

        self.assertFalse(booked_slot["is_available"])

        self.assertFalse(booked_slot["is_past"])

    # ANONYMOUS USER CANNOT BOOK

    def test_anonymous_user_cannot_book_appointment(self):
        url = reverse(
            "appointment:book-appointment",
            kwargs={
                "doctor_pk": self.doctor.pk,
            },
        )

        response = self.client.post(url,{"start_time": self.future_start.isoformat()})

        expected_login_url = (f"{settings.LOGIN_URL}?next={url}")

        self.assertRedirects(response,expected_login_url)

        self.assertEqual(Appointment.objects.count(),0)

    # NON-PATIENT USER WILL REDIRECT

    def test_non_patient_user_cannot_book_appointment(self):
        # Doctor user is authenticated,
        # but does not have a Patient profile.
        self.client.force_login( self.doctor_user)

        url = reverse("appointment:book-appointment", kwargs={"doctor_pk": self.doctor.pk})

        response = self.client.post(url,{"start_time": self.future_start.isoformat()})

        self.assertEqual(response.status_code,302)

        self.assertEqual(Appointment.objects.count(),0)

    # INSUFFICIENT WALLET BALANCE

    def test_booking_fails_when_wallet_balance_is_not_enough(self):
        self.login_patient()

        self.wallet.balance = Decimal("100.00")

        self.wallet.save(update_fields=["balance"])

        url = reverse("appointment:book-appointment",kwargs={"doctor_pk": self.doctor.pk})

        response = self.client.post(url,{"start_time": self.future_start.isoformat()})

        expected_url = reverse(
            "appointment:doctor-appointment-times",
            kwargs={
                "doctor_pk": self.doctor.pk,
                "date": self.future_date.strftime(
                    "%Y-%m-%d"
                ),
            },
        )

        self.assertRedirects(response,expected_url)

        self.wallet.refresh_from_db()

        self.assertEqual(self.wallet.balance,Decimal("100.00"))

        self.assertEqual(Appointment.objects.count(),0)

        self.assertEqual(Transaction.objects.count(),0)

    # INVALID WORKING TIME

    def test_booking_fails_for_invalid_working_time(self):
        self.login_patient()

        invalid_start = timezone.make_aware(
            datetime.combine(self.future_date,datetime.strptime("14:00","%H:%M").time()))

        url = reverse("appointment:book-appointment",kwargs={"doctor_pk": self.doctor.pk})

        response = self.client.post(url,{"start_time": invalid_start.isoformat()})

        expected_url = reverse(
            "appointment:doctor-appointment-times",
            kwargs={
                "doctor_pk": self.doctor.pk,
                "date": self.future_date.strftime("%Y-%m-%d")}
        )

        self.assertRedirects(response,expected_url)

        self.assertEqual(Appointment.objects.count(),0)

    # SUCCESSFUL BOOKING


    def test_successful_booking_creates_appointment_and_payment(self):
        self.login_patient()

        initial_balance = self.wallet.balance

        url = reverse(
            "appointment:book-appointment",
            kwargs={"doctor_pk": self.doctor.pk}
        )

        response = self.client.post(url,{"start_time": self.future_start.isoformat()})

        self.assertEqual(response.status_code,200)

        self.assertTemplateUsed(response,"appointment/booking_success.html")

        # Appointment
        appointment = Appointment.objects.get()

        self.assertEqual(appointment.patient,self.patient)

        self.assertEqual(appointment.doctor,self.doctor)

        self.assertEqual(appointment.start_time,self.future_start)

        self.assertEqual(appointment.end_time,self.future_start + timedelta(minutes=30))

        self.assertEqual(appointment.booking_status,"confirmed")

        self.assertEqual(appointment.visit_status,"absent")

        # Wallet

        self.wallet.refresh_from_db()

        expected_balance = initial_balance - self.doctor.visit_fee

        self.assertEqual(self.wallet.balance,expected_balance)

        # Transaction

        transaction = Transaction.objects.get(appointment=appointment)

        self.assertEqual(transaction.wallet,self.wallet)

        self.assertEqual(transaction.amount,self.doctor.visit_fee)

        self.assertEqual(transaction.type,"payment")

        self.assertIn("Appointment payment",transaction.description)

    # DUPLICATE APPOINTMENT

    def test_duplicate_booking_is_rejected(self):
        self.login_patient()

        # First patient has already booked this slot.
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            start_time=self.future_start,
            end_time=self.future_start + timedelta(minutes=30),
            booking_status="confirmed",
            visit_status="absent",
        )

        initial_balance = self.wallet.balance

        url = reverse("appointment:book-appointment",kwargs={"doctor_pk": self.doctor.pk})

        response = self.client.post(url,{"start_time": self.future_start.isoformat()})

        expected_url = reverse(
            "appointment:doctor-appointment-times",
            kwargs={
                "doctor_pk": self.doctor.pk,
                "date": self.future_date.strftime("%Y-%m-%d")}
        )

        self.assertRedirects(response,expected_url)

        # Still only one appointment.
        self.assertEqual(Appointment.objects.count(),1)

        self.wallet.refresh_from_db()

        # No money should be deducted.
        self.assertEqual(self.wallet.balance,initial_balance)

        # No transaction should be created.
        self.assertEqual(Transaction.objects.count(),0)

    # MY APPOINTMENTS

    def test_my_appointments_separates_appointments_and_feedback_status(self):
        self.login_patient()

        # Visited appointment without feedback

        visited_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=2) + timedelta(minutes=30),
            booking_status="confirmed",
            visit_status="visited",
        )

        # Upcoming appointment

        upcoming_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2) + timedelta(minutes=30),
            booking_status="confirmed",
            visit_status="absent",
        )
        # Visited appointment with feedback

        feedback_appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            start_time=timezone.now() - timedelta(days=5),
            end_time=timezone.now() - timedelta(days=5) + timedelta(minutes=30),
            booking_status="confirmed",
            visit_status="visited",
        )

        Feedback.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment=feedback_appointment,
            comment="Very good doctor and professional service.",
            rate=Feedback.Rate.EXCELLENT,
            is_confirmed=True,
        )

        url = reverse("appointment:my-appointments")

        response = self.client.get(url)

        self.assertEqual(response.status_code,200)

        self.assertTemplateUsed(response,"appointment/my_appointments.html")

        upcoming = response.context["upcoming_appointments"]

        past = response.context["past_appointments"]

        self.assertEqual(len(upcoming),1)

        self.assertEqual(upcoming[0]["appointment"],upcoming_appointment)

        self.assertFalse(upcoming[0]["can_submit_feedback"])

        self.assertEqual(len(past),2)

        visited_item = next(
            item
            for item in past
            if item["appointment"] == visited_appointment)

        feedback_item = next(
            item
            for item in past
            if item["appointment"] == feedback_appointment)

        # Visited but no feedback yet
        self.assertTrue(visited_item["is_visited"])

        self.assertFalse(visited_item["has_feedback"])

        self.assertTrue(visited_item["can_submit_feedback"])

        # Feedback already exists
        self.assertTrue(feedback_item["is_visited"])

        self.assertTrue(feedback_item["has_feedback"])

        self.assertFalse(feedback_item["can_submit_feedback"])

