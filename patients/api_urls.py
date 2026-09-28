from rest_framework.routers import DefaultRouter

from .api import MyAppointmentViewSet, PatientViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="api-patient")
router.register(r"my-appointments", MyAppointmentViewSet, basename="api-my-appointment")
urlpatterns = router.urls
