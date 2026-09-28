"""Tests for Nidaan — weighted towards the risky paths: money, invariants and access.

Run with:  python manage.py test
(Use Python 3.12 or 3.13; Django 5.1's test runner has a template-instrumentation
incompatibility on 3.14.)
"""
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import Appointment, Doctor, Patient, Payment

User = get_user_model()


# --- factories -------------------------------------------------------------
class DoctorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Doctor

    name = factory.Sequence(lambda n: f"Doc{n}")
    specialisation = "General"


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    name = factory.Sequence(lambda n: f"Patient {n}")
    phone = factory.Sequence(lambda n: f"09810000{n:03d}")
    city = "Pune"


class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment

    patient = factory.SubFactory(PatientFactory)
    doctor = factory.SubFactory(DoctorFactory)
    scheduled_for = factory.LazyFunction(timezone.now)


# --- model / business-logic tests -----------------------------------------
class AppointmentModelTests(TestCase):
    def test_str_and_manager_booked(self):
        doctor = DoctorFactory()
        for _ in range(3):
            AppointmentFactory(doctor=doctor, patient=PatientFactory(),
                               status=Appointment.Status.BOOKED)
        AppointmentFactory(doctor=doctor, patient=PatientFactory(),
                           status=Appointment.Status.DONE)
        self.assertEqual(Appointment.objects.booked().count(), 3)

    def test_complete_sets_status_fee_and_payment(self):
        appt = AppointmentFactory(status=Appointment.Status.BOOKED)
        appt.complete()
        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.Status.DONE)
        self.assertTrue(appt.fee > 0)
        self.assertTrue(Payment.objects.filter(appointment=appt).exists())

    def test_negative_fee_is_rejected(self):
        with self.assertRaises(IntegrityError):
            AppointmentFactory(fee=Decimal("-1"))

    def test_double_booking_is_rejected(self):
        slot = timezone.now()
        doctor = DoctorFactory()
        AppointmentFactory(doctor=doctor, scheduled_for=slot)
        with self.assertRaises(IntegrityError):
            AppointmentFactory(doctor=doctor, scheduled_for=slot)


class VisibilityTests(TestCase):
    def test_patient_sees_only_own_appointments(self):
        alice = User.objects.create_user("alice", password="pw-123456")
        mine = PatientFactory(user=alice)
        AppointmentFactory(patient=mine)
        AppointmentFactory(patient=PatientFactory())          # someone else's
        visible = Appointment.objects.visible_to(alice)
        self.assertEqual(visible.count(), 1)

    def test_staff_sees_all_appointments(self):
        staff = User.objects.create_user("staff", password="pw-123456", is_staff=True)
        AppointmentFactory()
        AppointmentFactory()
        self.assertEqual(Appointment.objects.visible_to(staff).count(), 2)
