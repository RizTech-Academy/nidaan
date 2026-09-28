"""Seed sample data so the app is populated to explore.

    python manage.py seed
"""
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from patients.models import Appointment, Doctor, Patient


class Command(BaseCommand):
    help = "Create sample doctors, patients and appointments."

    def handle(self, *args, **options):
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        Doctor.objects.all().delete()

        rao = Doctor.objects.create(name="Rao", specialisation="Cardiology",
                                    standard_fee=Decimal("800"))
        iyer = Doctor.objects.create(name="Iyer", specialisation="Pathology",
                                     standard_fee=Decimal("500"))

        cities = ["Pune", "Mumbai", "Pune", "Nagpur", "Pune", "Mumbai"]
        now = timezone.now()
        for i, city in enumerate(cities):
            patient = Patient.objects.create(
                name=f"Patient {i}", phone=f"09810000{i:03d}", city=city,
            )
            Appointment.objects.create(
                patient=patient,
                doctor=rao if i % 2 == 0 else iyer,
                scheduled_for=now + timedelta(days=i, hours=i),
                fee=Decimal("500") + i * 100,
                status=Appointment.Status.BOOKED if i % 2 == 0 else Appointment.Status.DONE,
            )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Doctor.objects.count()} doctors, "
            f"{Patient.objects.count()} patients, "
            f"{Appointment.objects.count()} appointments."
        ))
