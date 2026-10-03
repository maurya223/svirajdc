from django.contrib import admin
from .models import Contact, Appointment, Feedback, DoctorProfile


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "subject", "date")
    search_fields = ("name", "email", "phone", "subject", "message")
    list_filter = ("date",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "date",
        "time",
        "service",
        "amount",
        "status",
        "paid",
        "date_created",
    )
    search_fields = ("name", "email", "phone", "message")
    list_filter = ("status", "paid", "service", "date")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "rating",
        "is_approved",
        "date_created",
    )
    search_fields = ("name", "email", "message")
    list_filter = ("rating", "is_approved")


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "qualification",
        "specialization",
        "experience",
        "is_approved",
        "updated_at",
    )
    search_fields = ("name", "qualification", "specialization")
    list_filter = ("is_approved",)