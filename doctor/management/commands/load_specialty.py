from django.core.management.base import BaseCommand
from doctor.models import Specialty
from django.db import transaction
from django.utils.text import slugify

class Command(BaseCommand):
    help = " Add a standard catalog of medical specialties to database ."

    # Curated medical specialty dataset
    SPECIALTIES_DATA = [
        {
            "name": "Cardiology",
            "description": "Disorders of the heart and the cardiovascular system.",
            "icon": "heart-pulse",
        },
        {
            "name": "Dermatology",
            "description": "Conditions, diseases, and cosmetic issues of the skin, hair, and nails.",
            "icon": "sparkles",
        },
        {
            "name": "Neurology",
            "description": "Disorders of the nervous system, brain, and spinal cord.",
            "icon": "brain",
        },
        {
            "name": "Pediatrics",
            "description": "Medical care of infants, children, adolescents, and young adults.",
            "icon": "baby",
        },
        {
            "name": "Orthopedics",
            "description": "Conditions of the musculoskeletal system (bones, joints, ligaments, tendons).",
            "icon": "bone",
        },
        {
            "name": "Psychiatry",
            "description": "Diagnosis, prevention, and treatment of mental, emotional, and behavioral disorders.",
            "icon": "smile-plus",
        },
        {
            "name": "Ophthalmology",
            "description": "Eye and vision care, including surgical and medical treatments.",
            "icon": "eye",
        },
        {
            "name": "Obstetrics and Gynecology",
            "description": "Female reproductive health, pregnancy, childbirth, and postpartum care.",
            "icon": "user-check",
        },
        {
            "name": "General Surgery",
            "description": "Surgical treatment of abdominal organs, trauma, and soft tissues.",
            "icon": "scissors",
        },
        {
            "name": "Internal Medicine",
            "description": "Comprehensive prevention, diagnosis, and treatment of adult diseases.",
            "icon": "stethoscope",
        },
        {
            "name": "Gastroenterology",
            "description": "Digestive system disorders involving the stomach, intestines, liver, and pancreas.",
            "icon": "activity",
        },
        {
            "name": "Endocrinology",
            "description": "Hormonal, gland, and metabolic conditions such as diabetes and thyroid disorders.",
            "icon": "flame",
        },
        {
            "name": "Pulmonology",
            "description": "Diseases and physiological conditions of the respiratory tract and lungs.",
            "icon": "wind",
        },
        {
            "name": "Urology",
            "description": "Diseases of the urinary tract system and the male reproductive system.",
            "icon": "droplet",
        },
        {
            "name": "Nephrology",
            "description": "Specialized kidney physiology, care, and kidney disease treatments.",
            "icon": "shield-plus",
        },
        {
            "name": "Otolaryngology (ENT)",
            "description": "Medical and surgical management of ear, nose, and throat disorders.",
            "icon": "ear",
        },
        {
            "name": "Oncology",
            "description": "Investigation, diagnosis, and treatment of benign and malignant tumors/cancer.",
            "icon": "crosshair",
        },
        {
            "name": "Rheumatology",
            "description": "Autoimmune and inflammatory diseases of joints, muscles, and bones.",
            "icon": "shield-alert",
        },
        {
            "name": "Allergy and Immunology",
            "description": "Disorders related to immune response malfunctions and allergic conditions.",
            "icon": "alert-circle",
        },
        {
            "name": "Infectious Disease",
            "description": "Complex illnesses caused by bacteria, viruses, fungi, or parasites.",
            "icon": "bug",
        },
        {
            "name": "Physical Medicine and Rehabilitation",
            "description": "Restoration of functional ability and quality of life for physical impairments.",
            "icon": "activity",
        },
        {
            "name": "Geriatrics",
            "description": "Healthcare focused on the unique needs and wellness of elderly adults.",
            "icon": "users",
        },
        {
            "name": "Hematology",
            "description": "Diseases related to blood, blood-forming organs, and blood disorders.",
            "icon": "droplets",
        },
        {
            "name": "Anesthesiology",
            "description": "Perioperative care, anesthesia administration, and chronic pain management.",
            "icon": "syringe",
        },
        {
            "name": "Radiology",
            "description": "Medical imaging technologies for diagnosing and treating diseases.",
            "icon": "scan",
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Wipe all existing specialties prior to seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            count, _ = Specialty.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Purged {count} existing specialty records.")
            )

        created_count = 0
        updated_count = 0

        self.stdout.write(self.style.HTTP_INFO("Seeding specialties into database..."))

        for title in self.SPECIALTIES_DATA:
            slug = slugify(title,allow_unicode=True)
            specialty, created = Specialty.objects.update_or_create(
                slug=slug,
                defaults={"title":title},
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
               f"Successfully created {created_count} | "
               f"updated: {updated_count} | "
               f"total in database {Specialty.objects.count()}"
            )
        )