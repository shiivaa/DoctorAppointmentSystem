from django.test import TestCase

from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.utils import IntegrityError

from feedback.models import Feedback
from feedback.forms import FeedbackForm
from feedback import services
from user.models import Patient
from doctor.models import Doctor
from appointment.models import Appointment

User = get_user_model()


class FeedbackBaseTestCase(TestCase):
    

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="patient1", password="password123", email="p1@example.com"
        )
        self.patient1 = Patient.objects.create(user=self.user1)

       
        self.user2 = User.objects.create_user(
            username="patient2", password="password123", email="p2@example.com"
        )
        self.patient2 = Patient.objects.create(user=self.user2)

       
        self.regular_user = User.objects.create_user(
            username="regular", password="password123", email="reg@example.com"
        )

       
        self.doctor_user = User.objects.create_user(
            username="doctor1", password="password123", email="doc@example.com"
        )
        self.doctor = Doctor.objects.create(user=self.doctor_user)

       
        self.past_appointment = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=2, hours=-1)
        )

        self.future_appointment = Appointment.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1)
        )



class FeedbackModelTest(FeedbackBaseTestCase):

    def test_feedback_string_representation(self):
        feedback = Feedback.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment,
            rate=Feedback.Rate.GOOD,
            comment="Dr. was very polite."
        )
        expected_str = f"Feedback By {self.patient1} for {self.doctor}  : rate {Feedback.Rate.GOOD}"
        self.assertEqual(str(feedback), expected_str)

    def test_default_values(self):
        feedback = Feedback.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment
        )
        self.assertEqual(feedback.rate, Feedback.Rate.AVERAGE)
        self.assertFalse(feedback.is_confirmed)
        self.assertEqual(feedback.comment, "")

    def test_rate_validators(self):
        
        feedback_low = Feedback(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment,
            rate=0
        )
        with self.assertRaises(ValidationError):
            feedback_low.full_clean()


        feedback_high = Feedback(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment,
            rate=6
        )
        with self.assertRaises(ValidationError):
            feedback_high.full_clean()

    def test_unique_feedback_per_appointment_constraint(self):
      
        Feedback.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment,
            rate=Feedback.Rate.EXCELLENT
        )

       
        with self.assertRaises(IntegrityError):
            Feedback.objects.create(
                patient=self.patient1,
                doctor=self.doctor,
                appointment=self.past_appointment,
                rate=Feedback.Rate.POOR
            )



class FeedbackFormTest(TestCase):

    def test_valid_form_data(self):
        form = FeedbackForm(data={
            'rate': Feedback.Rate.GOOD,
            'comment': 'Clean clinic and short waiting time.'
        })
        self.assertTrue(form.is_valid())

    def test_form_comment_optional(self):
        form = FeedbackForm(data={'rate': Feedback.Rate.AVERAGE, 'comment': ''})
        self.assertTrue(form.is_valid())

    def test_form_invalid_rate(self):
        form = FeedbackForm(data={'rate': 99, 'comment': 'Invalid'})
        self.assertFalse(form.is_valid())
        self.assertIn('rate', form.errors)

    def test_form_comment_max_length(self):
        form = FeedbackForm(data={
            'rate': 5,
            'comment': 'x' * 401  
        })
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)



class FeedbackServicesTest(FeedbackBaseTestCase):

    def test_can_submit_feedback_successfully(self):
        can_submit = services.can_patient_submit_feedback(
            patient=self.patient1,
            appointment=self.past_appointment
        )
        self.assertTrue(can_submit)

    def test_cannot_submit_feedback_for_another_patient(self):

        with self.assertRaises(PermissionDenied) as ctx:
            services.can_patient_submit_feedback(
                patient=self.patient2,
                appointment=self.past_appointment
            )
        self.assertIn("You are not allowed to leave feedback for this appointment.", str(ctx.exception))

    def test_cannot_submit_feedback_for_future_appointment(self):
     
        with self.assertRaises(PermissionDenied) as ctx:
            services.can_patient_submit_feedback(
                patient=self.patient1,
                appointment=self.future_appointment
            )
        self.assertIn("You can only leave feedback for past appointments.", str(ctx.exception))

    def test_cannot_submit_feedback_twice(self):
        
        Feedback.objects.create(
            patient=self.patient1,
            doctor=self.doctor,
            appointment=self.past_appointment,
            rate=Feedback.Rate.EXCELLENT
        )
 
        with self.assertRaises(PermissionDenied) as ctx:
            services.can_patient_submit_feedback(
                patient=self.patient1,
                appointment=self.past_appointment
            )
        self.assertIn("One feedback has already been submitted for this appointment.", str(ctx.exception))

    def test_get_doctor_average_rating(self):
        
        self.assertEqual(services.get_doctor_average_rating(self.doctor), 0.0)

    
        Feedback.objects.create(
            patient=self.patient1, doctor=self.doctor,
            rate=1, is_confirmed=False
        )

        Feedback.objects.create(
            patient=self.patient1, doctor=self.doctor,
            rate=5, is_confirmed=True
        )
        Feedback.objects.create(
            patient=self.patient2, doctor=self.doctor,
            rate=4, is_confirmed=True
        )

        avg = services.get_doctor_average_rating(self.doctor)
        self.assertEqual(avg, 4.5)



class FeedbackViewTests(FeedbackBaseTestCase):

    def test_create_view_anonymous_redirects_to_login(self):
        url = reverse('feedback:add_feedback', kwargs={'appointment_pk': self.past_appointment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_view_non_patient_user_forbidden(self):
        self.client.force_login(self.regular_user)
        url = reverse('feedback:add_feedback', kwargs={'appointment_pk': self.past_appointment.pk})
        response = self.client.get(url)
      
        self.assertEqual(response.status_code, 403)

    def test_create_view_permission_denied_redirects_with_message(self):
    
        self.client.force_login(self.user2)
        url = reverse('feedback:add_feedback', kwargs={'appointment_pk': self.past_appointment.pk})
        response = self.client.get(url)

     
        self.assertRedirects(response, reverse('appointments:my_appointments'))

    def test_create_view_get_success(self):
        self.client.force_login(self.user1)
        url = reverse('feedback:add_feedback', kwargs={'appointment_pk': self.past_appointment.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedback/feedback_form.html')
        self.assertIsInstance(response.context['form'], FeedbackForm)

    def test_create_view_post_success(self):
        self.client.force_login(self.user1)
        url = reverse('feedback:add_feedback', kwargs={'appointment_pk': self.past_appointment.pk})
        post_data = {
            'rate': Feedback.Rate.EXCELLENT,
            'comment': 'Exceptional care!'
        }
        response = self.client.post(url, post_data)

      
        self.assertRedirects(response, reverse('appointments:my_appointments'))

  
        feedback = Feedback.objects.get(appointment=self.past_appointment)
        self.assertEqual(feedback.rate, Feedback.Rate.EXCELLENT)
        self.assertEqual(feedback.comment, 'Exceptional care!')
        self.assertEqual(feedback.patient, self.patient1)
        self.assertEqual(feedback.doctor, self.doctor)
        self.assertFalse(feedback.is_confirmed)  

    def test_doctor_feedback_list_view(self):
       
        Feedback.objects.create(patient=self.patient1, doctor=self.doctor, rate=5, is_confirmed=True, comment="Great")
        Feedback.objects.create(patient=self.patient2, doctor=self.doctor, rate=4, is_confirmed=True, comment="Good")
        Feedback.objects.create(patient=self.patient1, doctor=self.doctor, rate=1, is_confirmed=False, comment="Pending")

        url = reverse('feedback:show_feedbacks', kwargs={'doctor_pk': self.doctor.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedback/doctor_feedback_list.html')
      
        feedbacks = response.context['feedbacks']
        self.assertEqual(len(feedbacks), 2)
        self.assertEqual(response.context['average_rating'], 4.5)