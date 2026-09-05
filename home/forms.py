from django import forms
from .models import Contact, Appointment, Feedback,DoctorProfile


from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "subject", "message"]


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "name",
            "email",
            "phone",
            "date",
            "time",
            "service",
            "message",
        ]


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "email", "message", "rating"]
class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            "name",
            "qualification",
            "specialization",
            "experience",
            "bio",
            "image",
        ]