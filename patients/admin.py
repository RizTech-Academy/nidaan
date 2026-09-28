from django.contrib import admin

from .models import Appointment, Doctor, Patient, Payment, TestReport


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "created_at")
    list_filter = ("city",)
    search_fields = ("name", "phone")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialisation", "standard_fee")
    search_fields = ("name", "specialisation")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "scheduled_for", "status", "fee")
    list_filter = ("status", "doctor")
    date_hierarchy = "scheduled_for"
    autocomplete_fields = ("patient",)
    list_select_related = ("patient", "doctor")     # no N+1 in the list view


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ("test_name", "patient", "reported_at")
    list_filter = ("test_name",)
    search_fields = ("test_name", "patient__name")
    list_select_related = ("patient",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("appointment", "amount", "paid_at")
    list_select_related = ("appointment",)
