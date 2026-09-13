import os
import django
from datetime import date, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from doctor.models import Doctor, Specialty, WorkingShift


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


print()
print("===================================")
print("Seed completed successfully!")
print("30 doctors created/verified.")
print("Each doctor has 2 working shifts.")
print("Default doctor password: Doctor12345")
print("===================================")