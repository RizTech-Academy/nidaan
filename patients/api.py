from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Appointment, Patient
from .serializers import AppointmentSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """Staff-facing CRUD over patients (requires authentication)."""
    queryset = Patient.objects.all().order_by("name")
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "phone"]
    ordering_fields = ["name", "city"]


class MyAppointmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Patient-facing: a logged-in user sees ONLY their own appointments.

    Object-level access enforced by scoping the queryset to the requesting user —
    forbidden records are never in the result set (see the capstone access lesson).
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Appointment.objects
            .visible_to(self.request.user)
            .select_related("patient", "doctor")     # no N+1 in the API either
            .order_by("-scheduled_for")
        )
