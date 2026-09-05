
from django.contrib import admin
from .models import Contact, Appointment, Feedback, DoctorProfile


admin.site.register(Contact)
admin.site.register(Appointment)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "message",
        "rating",
        "is_approved",
        "date_created",
    )

    search_fields = (
        "name",
        "email",
        "message",
    )

    list_filter = (
        "rating",
        "is_approved",
        "date_created",
    )

# =========================
# DOCTOR PROFILE
# =========================

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "qualification",
        "specialization",
        "experience",
        "is_approved",
        "updated_at",
    )

    search_fields = (
        "name",
        "qualification",
        "specialization",
    )

    list_filter = (
        "is_approved",
        "specialization",
    )

    # Admin list page par directly approval kar sakte ho
    list_editable = (
        "is_approved",
    )
