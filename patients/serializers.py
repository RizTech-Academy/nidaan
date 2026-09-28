from rest_framework import serializers

from .models import Appointment, Patient, TestReport


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "phone", "city"]

    def validate_phone(self, value):
        digits = value.lstrip("+").replace(" ", "")
        if not digits.isdigit() or len(digits) < 10:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id", "patient", "patient_name", "doctor", "doctor_name",
                  "scheduled_for", "status", "fee"]


class TestReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestReport
        fields = ["id", "patient", "test_name", "result", "reported_at"]
