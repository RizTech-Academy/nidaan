from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Patient
from .forms import PatientForm


def patient_list(request):
    city = request.GET.get("city", "Pune")
    patients = Patient.objects.filter(city=city).order_by("name")
    return render(request, "patients/patient_list.html", {"patients": patients, "city": city})


def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Added {patient.name}.")
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form})
