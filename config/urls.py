from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/", include("patients.api_urls")),
    path("admin/", admin.site.urls),
    path("patients/", include("patients.urls")),
]
