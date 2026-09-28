from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "phone", "city"]

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        digits = phone.lstrip("+").replace(" ", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("Enter a valid phone number (at least 10 digits).")
        return phone
