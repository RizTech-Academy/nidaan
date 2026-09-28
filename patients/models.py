"""Nidaan domain models: doctors, patients, appointments, test reports and payments.

The data layer for a clinic and diagnostic-lab manager. Field types, relationships,
`on_delete` choices and constraints are all deliberate — see the Django Web Development
course, module "The ORM in Depth" and the capstone.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialisation = models.CharField(max_length=100)
    standard_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("500"))

    def __str__(self):
        return f"Dr {self.name}"


class Patient(models.Model):
    # Linked to a user account so a patient can be given read-only API access to
    # their own records (see the API + access lessons). Optional: staff-created
    # patients may not have a login.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="patient_profile",
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)          # CharField, not integer: leading zeros, +91
    city = models.CharField(max_length=60)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["city"])]    # staff filter by city constantly

    def __str__(self):
        return self.name


class AppointmentQuerySet(models.QuerySet):
    def booked(self):
        return self.filter(status=Appointment.Status.BOOKED)

    def for_city(self, city):
        return self.filter(patient__city=city)

    def visible_to(self, user):
        """Object-level scoping: staff see everything, a patient sees only their own."""
        if user.is_staff:
            return self
        return self.filter(patient__user=user)


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments")
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0"))

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(fee__gte=0), name="fee_non_negative"),
            models.UniqueConstraint(fields=["doctor", "scheduled_for"], name="no_double_booking"),
        ]

    def __str__(self):
        return f"{self.patient} with {self.doctor}"

    def _fee_for_patient(self):
        base = self.doctor.standard_fee
        completed = self.patient.appointments.filter(status=self.Status.DONE).count()
        return base * Decimal("0.9") if completed >= 5 else base   # loyalty discount

    def complete(self):
        """Mark done, set the fee, and record the payment — atomically."""
        with transaction.atomic():
            self.status = self.Status.DONE
            self.fee = self._fee_for_patient()
            self.save()
            Payment.objects.create(appointment=self, amount=self.fee)


class TestReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="reports")
    # A report outlives the appointment it came from, so SET_NULL, not CASCADE.
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports",
    )
    test_name = models.CharField(max_length=120)
    result = models.TextField(blank=True)
    scan = models.FileField(upload_to="reports/%Y/%m/", blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_name} for {self.patient}"


class Payment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name="payment_non_negative"),
        ]

    def __str__(self):
        return f"₹{self.amount} for {self.appointment}"
