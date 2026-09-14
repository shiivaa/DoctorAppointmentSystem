from datetime import time
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from .models import Doctor, Specialty, WorkingShift
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class SpecialtyModelTest(TestCase):
    def test_create_specialty_and_str(self):
        specialty = Specialty.objects.create(title="Cardiology", slug="cardiology")
        self.assertEqual(str(specialty), "Cardiology")


    def test_specialty_unique_fields(self):
        Specialty.objects.create(title="Cardiology", slug="cardiology")
        with self.assertRaises(IntegrityError):
            Specialty.objects.create(title="Cardiology", slug="cardiology-2")


class DoctorModelTest(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.create(title="Cardiology", slug="cardiology")
        self.user_with_name = User.objects.create_user(
            username="dr_john",
            email="john@example.com",
            password="securepassword123",
            first_name="John",
            last_name="Doe",
        )
        self.user_without_name = User.objects.create_user(
            username="dr_jane",
            email="jane@example.com",
            password="securepassword123",
        )


    def test_doctor_str_with_full_name(self):
        doctor = Doctor.objects.create(
            user=self.user_with_name,
            specialty=self.specialty,
            medical_license_number="12345",
        )
        self.assertEqual(str(doctor), "Dr. John Doe")


    def test_doctor_str_fallback_to_username(self):
        doctor = Doctor.objects.create(
            user=self.user_without_name,
            specialty=self.specialty,
            medical_license_number="67890",
        )
        self.assertEqual(str(doctor), "Dr. dr_jane")


    def test_doctor_medical_license_unique(self):
        Doctor.objects.create(
            user=self.user_with_name,
            specialty=self.specialty,
            medical_license_number="12345",
        )
        with self.assertRaises(IntegrityError):
            Doctor.objects.create(
                user=self.user_without_name,
                specialty=self.specialty,
                medical_license_number="12345",
            )


class WorkingShiftModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="doc1",
            email="doc1@example.com",
            first_name="Ali",
            last_name="Rezaei",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            username="doc2",
            email="doc2@example.com",
            first_name="Sara",
            last_name="Ahmadi",
            password="password123",
        )
        self.doctor1 = Doctor.objects.create(
            user=self.user1,
            medical_license_number="DOC-01",
            visit_duration=30,
        )
        self.doctor2 = Doctor.objects.create(
            user=self.user2,
            medical_license_number="DOC-02",
            visit_duration=30,
        )


    def test_valid_shift_creation(self):
        shift = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        shift.full_clean()
        shift.save()
        self.assertEqual(WorkingShift.objects.count(), 1)


    def test_end_time_must_be_after_start_time(self):
        shift1 = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(14, 0),
            end_time=time(13, 0),
        )
        with self.assertRaises(ValidationError) as ctx:
            shift1.full_clean()
        self.assertIn("end_time", ctx.exception.message_dict)

        shift2 = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(10, 0),
            end_time=time(10, 0),
        )
        with self.assertRaises(ValidationError) as ctx:
            shift2.full_clean()
        self.assertIn("end_time", ctx.exception.message_dict)


    def test_shift_duration_less_than_visit_duration(self):
        shift = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(10, 0),
            end_time=time(10, 20),
        )
        with self.assertRaises(ValidationError) as ctx:
            shift.full_clean()
        self.assertIn("Duration cannot be less than 30 minutes", str(ctx.exception))


    def test_shift_overlap_for_same_doctor_and_same_day(self):
        WorkingShift.objects.create(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

        overlapping_shift = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(11, 0),
            end_time=time(13, 0),
        )
        with self.assertRaises(ValidationError) as ctx:
            overlapping_shift.full_clean()
        self.assertIn("This time overlaps with the others.", str(ctx.exception))

        inner_shift = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 30),
            end_time=time(10, 30),
        )
        with self.assertRaises(ValidationError) as ctx:
            inner_shift.full_clean()
        self.assertIn("This time overlaps with the others.", str(ctx.exception))


    def test_no_overlap_for_different_days_or_different_doctors(self):
        WorkingShift.objects.create(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        shift_other_day = WorkingShift(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SUNDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        shift_other_day.full_clean()
        shift_other_day.save()

        shift_other_doctor = WorkingShift(
            doctor=self.doctor2,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        shift_other_doctor.full_clean()
        shift_other_doctor.save()
        self.assertEqual(WorkingShift.objects.count(), 3)


    def test_update_existing_shift_without_self_overlap(self):
        shift = WorkingShift.objects.create(
            doctor=self.doctor1,
            day_of_week=WorkingShift.Weekday.SATURDAY,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        shift.end_time = time(13, 0)
        shift.full_clean()
        shift.save()
        shift.refresh_from_db()
        self.assertEqual(shift.end_time, time(13, 0))


#---------------------------------------------------------------------------------
#--------------------------------------views--------------------------------------
#---------------------------------------------------------------------------------


class DoctorListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.specialty_cardio = Specialty.objects.create(
            title="Cardiology", slug="cardiology"
        )
        self.specialty_derma = Specialty.objects.create(
            title="Dermatology", slug="dermatology"
        )
        self.user1 = User.objects.create_user(
            username="dr_ali",
            email="ali@example.com",
            first_name="Ali",
            last_name="Rezaei",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            username="dr_sara",
            email="sara@example.com",
            first_name="Sara",
            last_name="Ahmadi",
            password="password123",
        )
        self.doctor1 = Doctor.objects.create(
            user=self.user1,
            specialty=self.specialty_cardio,
            medical_license_number="LIC-101",
            visit_fee=Decimal("150000"),
        )
        self.doctor2 = Doctor.objects.create(
            user=self.user2,
            specialty=self.specialty_derma,
            medical_license_number="LIC-102",
            visit_fee=Decimal("250000"),
        )


    def test_doctor_list_view_status_and_template(self):
        response = self.client.get(reverse("doctor:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/doctor_list.html")
        self.assertIn("page_obj", response.context)
        self.assertIn("specialties", response.context)
        self.assertEqual(len(response.context["page_obj"]), 2)


    def test_doctor_list_search_by_first_name(self):
        response = self.client.get(reverse("doctor:list"), {"q": "Ali"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["page_obj"][0], self.doctor1)


    def test_doctor_list_search_by_specialty_title(self):
        response = self.client.get(reverse("doctor:list"), {"q": "Cardiology"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["page_obj"][0], self.doctor1)


    def test_doctor_list_filter_by_specialty_slug(self):
        response = self.client.get(
            reverse("doctor:list"), {"specialty": "dermatology"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["page_obj"][0], self.doctor2)


    def test_doctor_list_sorting_by_fee_asc(self):
        response = self.client.get(reverse("doctor:list"), {"sort": "fee"})
        self.assertEqual(response.status_code, 200)
        doctors = list(response.context["page_obj"])
        self.assertEqual(doctors[0], self.doctor1)
        self.assertEqual(doctors[1], self.doctor2)


    def test_doctor_list_sorting_by_fee_desc(self):
        response = self.client.get(reverse("doctor:list"), {"sort": "-fee"})
        self.assertEqual(response.status_code, 200)
        doctors = list(response.context["page_obj"])
        self.assertEqual(doctors[0], self.doctor2)
        self.assertEqual(doctors[1], self.doctor1)


class DoctorDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient_user = User.objects.create_user(
            username="patient1",
            email="patient@example.com",
            password="securepassword123",
        )
        self.doctor_user = User.objects.create_user(
            username="dr_reza",
            email="reza@example.com",
            first_name="Reza",
            last_name="Karimi",
            password="password123",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            medical_license_number="LIC-200",
            visit_fee=Decimal("180000"),
        )


    def test_doctor_detail_anonymous_user_redirects_to_login(self):
        url = reverse("doctor:detail", kwargs={"pk": self.doctor.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/user/sign-in/", response.url)


    def test_doctor_detail_authenticated_user_access_success(self):
        self.client.login(username="patient1", password="securepassword123")
        url = reverse("doctor:detail", kwargs={"pk": self.doctor.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor/doctor_detail.html")
        self.assertEqual(response.context["doctor"], self.doctor)


    def test_doctor_detail_not_found(self):
        self.client.login(username="patient1", password="securepassword123")
        url = reverse("doctor:detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

