import os
import django
from datetime import date, time, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from doctor.models import Doctor, Specialty, WorkingShift

from django.utils import timezone
from appointment.models import Appointment
from feedback.models import Feedback
from user.models import Patient


User = get_user_model()


SPECIALTIES = [
    ("Cardiology", "cardiology"),
    ("Dermatology", "dermatology"),
    ("Neurology", "neurology"),
    ("Pediatrics", "pediatrics"),
    ("Psychiatry", "psychiatry"),
    ("Orthopedics", "orthopedics"),
    ("Ophthalmology", "ophthalmology"),
    ("Dentistry", "dentistry"),
    ("Internal Medicine", "internal-medicine"),
    ("General Surgery", "general-surgery"),
]


DOCTORS = [
    ("Ali", "Ahmadi"),
    ("Reza", "Mohammadi"),
    ("Sara", "Karimi"),
    ("Maryam", "Hosseini"),
    ("Amir", "Rahimi"),
    ("Neda", "Moradi"),
    ("Mehdi", "Ebrahimi"),
    ("Zahra", "Jafari"),
    ("Arman", "Soleimani"),
    ("Fatemeh", "Rostami"),
    ("Sina", "Kazemi"),
    ("Leila", "Ahmadi"),
    ("Pouya", "Mohammadi"),
    ("Mina", "Karimi"),
    ("Hamid", "Hosseini"),
    ("Shirin", "Rahimi"),
    ("Omid", "Moradi"),
    ("Parisa", "Ebrahimi"),
    ("Navid", "Jafari"),
    ("Elham", "Soleimani"),
    ("Kian", "Rostami"),
    ("Nazanin", "Kazemi"),
    ("Milad", "Ahmadi"),
    ("Yasaman", "Mohammadi"),
    ("Soroush", "Karimi"),
    ("Hanieh", "Hosseini"),
    ("Farhad", "Rahimi"),
    ("Arezoo", "Moradi"),
    ("Shayan", "Ebrahimi"),
    ("Tara", "Jafari"),
]


# -----------------------------
# Create specialties
# -----------------------------

specialties = {}

for title, slug in SPECIALTIES:
    specialty, created = Specialty.objects.get_or_create(
        slug=slug,
        defaults={
            "title": title,
        }
    )

    specialties[slug] = specialty

    if created:
        print(f"Created specialty: {title}")
    else:
        print(f"Already exists: {title}")


# -----------------------------
# Create doctors
# -----------------------------

for index, (first_name, last_name) in enumerate(DOCTORS, start=1):

    username = f"doctor{index}"
    phone = f"989120000{index:03d}"
    email = f"doctor{index}@example.com"
    national_code = f"{1000000000 + index:010d}"
    medical_license = f"{1000000000 + index:010d}"

    specialty_list = list(specialties.values())
    specialty = specialty_list[(index - 1) % len(specialty_list)]

    user, user_created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email,
            "gender": "male" if index % 2 else "female",
            "national_code": national_code,
            "birth_date": date(1980 + (index % 15), 1 + (index % 12), 1 + (index % 25)),
        }
    )

    if user_created:
        user.set_password("Doctor12345")
        user.save()

        print(f"Created user: {username}")
    else:
        print(f"User already exists: {username}")

    doctor, doctor_created = Doctor.objects.get_or_create(
        user=user,
        defaults={
            "specialty": specialty,
            "medical_license_number": medical_license,
            "address": f"CarePoint Medical Center - Room {index}",
            "visit_fee": 500000 + (index * 50000),
            "visit_duration": [20, 30, 60][(index - 1) % 3],
            "bio": f"Experienced {specialty.title.lower()} specialist.",
        }
    )

    if doctor_created:
        print(f"Created doctor: Dr. {first_name} {last_name}")
    else:
        print(f"Doctor already exists: Dr. {first_name} {last_name}")


# -----------------------------
# Create working shifts
# -----------------------------

    shifts = [
        {
            "day_of_week": (index - 1) % 6,
            "start_time": time(9, 0),
            "end_time": time(13, 0),
        },
        {
            "day_of_week": ((index - 1) % 6 + 2) % 7,
            "start_time": time(15, 0),
            "end_time": time(19, 0),
        },
    ]

    for shift_data in shifts:
        shift, created = WorkingShift.objects.get_or_create(
            doctor=doctor,
            day_of_week=shift_data["day_of_week"],
            start_time=shift_data["start_time"],
            end_time=shift_data["end_time"],
        )

        if created:
            print(
                f"  Created shift: "
                f"{shift_data['day_of_week']} "
                f"{shift_data['start_time']} - "
                f"{shift_data['end_time']}"
            )


# -----------------------------
# Create patients
# -----------------------------

patients = []

for index in range(1, 11):

    username = f"patient{index}"
    phone = f"989130000{index:03d}"
    email = f"patient{index}@example.com"
    national_code = f"{2000000000 + index:010d}"
    insurance_number = f"{3000000000 + index:010d}"

    user, user_created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": f"Patient{index}",
            "last_name": "Test",
            "phone": phone,
            "email": email,
            "gender": "male" if index % 2 else "female",
            "national_code": national_code,
            "birth_date": date(
                1990 + (index % 10),
                1 + (index % 12),
                1 + (index % 25),
            ),
        }
    )

    if user_created:
        user.set_password("Patient12345")
        user.save()
        print(f"Created user: {username}")

    patient, patient_created = Patient.objects.get_or_create(
        user=user,
        defaults={
            "insurance_number": insurance_number,
            "address": f"Test address {index}",
        }
    )

    patients.append(patient)

    if patient_created:
        print(f"Created patient: {username}")


# -----------------------------
# Create past appointments
# -----------------------------

appointments = []

doctors = list(
    Doctor.objects.select_related("user").order_by("id")
)

base_time = timezone.now().replace(
    hour=9,
    minute=0,
    second=0,
    microsecond=0,
)

appointment_index = 0

for doctor in doctors:

    for feedback_number in range(3):

        patient = patients[appointment_index % len(patients)]

        start_time = base_time - timedelta(
            days=100 - appointment_index
        )

        end_time = start_time + timedelta(
            minutes=doctor.visit_duration
        )

        appointment, created = Appointment.objects.get_or_create(
            doctor=doctor,
            start_time=start_time,
            defaults={
                "patient": patient,
                "end_time": end_time,
                "booking_status": "confirmed",
                "visit_status": "visited",
            }
        )

        if not created:
            appointment.patient = patient
            appointment.end_time = end_time
            appointment.booking_status = "confirmed"
            appointment.visit_status = "visited"
            appointment.save()

        appointments.append(appointment)

        appointment_index += 1

        if created:
            print(
                f"Created appointment {appointment_index}: "
                f"{patient.user.username} -> "
                f"Dr. {doctor.user.get_full_name()}"
            )


# -----------------------------
# Create feedbacks
# -----------------------------

comments = [
    "Very professional and helpful.",
    "The doctor explained everything clearly.",
    "Good experience and friendly behavior.",
    "I was satisfied with the visit.",
    "Very knowledgeable doctor.",
    "The appointment went smoothly.",
    "Professional and respectful.",
    "Overall a very good experience.",
    "The doctor listened carefully to my concerns.",
    "I would recommend this doctor.",
]

feedback_count = 0

for index, appointment in enumerate(appointments):

    if Feedback.objects.filter(
        appointment=appointment
    ).exists():
        continue

    rate = [5, 4, 5, 4, 3][index % 5]

    Feedback.objects.create(
        patient=appointment.patient,
        doctor=appointment.doctor,
        appointment=appointment,
        rate=rate,
        comment=comments[index % len(comments)],
        is_confirmed=True,
    )

    feedback_count += 1

    print(
        f"Created feedback {feedback_count}: "
        f"{appointment.patient.user.username} -> "
        f"Dr. {appointment.doctor.user.get_full_name()}"
    )


print()
print("===================================")
print("Seed completed successfully!")
print("30 doctors created/verified.")
print("Each doctor has 2 working shifts.")
print("10 patients created/verified.")
print("90 past appointments created/verified.")
print(f"{feedback_count} new feedbacks created.")
print("Each doctor has 3 feedbacks.")
print("Default doctor password: Doctor12345")
print("Default patient password: Patient12345")
print("===================================")