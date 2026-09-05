from django.db import models
from django.utils import timezone

class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    phone = models.CharField(max_length=12)
    subject = models.CharField(max_length=122, blank=True)
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"

class Appointment(models.Model):
    SERVICES = [
        ('cleaning', 'Teeth Cleaning'),
        ('teeth_whitening', 'Teeth Whitening'),
        ('teeth_polishing', 'Teeth Polishing'),
        ('teeth_filling', 'Teeth Filling'),
        ('extraction', 'Tooth Extraction'),
        ('dental_implants', 'Dental Implants'),
        ('crown_and_bridge', 'Crown and Bridge'),
        ('complete_denture', 'Complete Denture'),
        ('orthodontics', 'Orthodontics'),
        ('root_canal_treatment', 'Root Canal Treatment(RCT)'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(blank=True, max_length=20)
    date = models.DateField()
    time = models.TimeField()
    service = models.CharField(max_length=50, choices=SERVICES, blank=True)
    amount = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=10)
    status = models.CharField(max_length=20, default='Pending')
    message = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Appointment by {self.name} on {self.date} at {self.time}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.name} - Rating: {self.rating}"

from django.db import models
from django.contrib.auth.models import User
class DoctorProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )

    name = models.CharField(max_length=100)

    qualification = models.CharField(
        max_length=200,
        blank=True
    )

    specialization = models.CharField(
        max_length=200,
        blank=True
    )

    experience = models.PositiveIntegerField(
        default=0
    )

    bio = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="doctors/",
        blank=True,
        null=True
    )

    is_approved = models.BooleanField(
        default=False
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

