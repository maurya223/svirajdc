from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import (
    Appointment,
    Contact,
    Feedback,
    DoctorProfile,
)

from .forms import (
    AppointmentForm,
    ContactForm,
    FeedbackForm,
)


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin / Superuser
            if user.is_superuser:
                return redirect("/admin/")

            # Normal Doctor
            return redirect("doctor_dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "login.html"
    )


# =========================================================
# DOCTOR REGISTER
# =========================================================

def doctor_register(request):

    if request.method == "POST":

        # -------------------------------------------------
        # Account Information
        # -------------------------------------------------

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # Doctor Information
        # -------------------------------------------------

        name = request.POST.get(
            "name",
            ""
        ).strip()

        qualification = request.POST.get(
            "qualification",
            ""
        ).strip()

        experience = request.POST.get(
            "experience",
            ""
        ).strip()

        specialization = request.POST.get(
            "specialization",
            ""
        ).strip()

        bio = request.POST.get(
            "bio",
            ""
        ).strip()

        image = request.FILES.get(
            "image"
        )

        # -------------------------------------------------
        # Basic Validation
        # -------------------------------------------------

        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return redirect(
                "doctor_register"
            )

        if not email:

            messages.error(
                request,
                "Email is required."
            )

            return redirect(
                "doctor_register"
            )

        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return redirect(
                "doctor_register"
            )

        if not name:

            messages.error(
                request,
                "Doctor name is required."
            )

            return redirect(
                "doctor_register"
            )

        # -------------------------------------------------
        # Username Check
        # -------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists!"
            )

            return redirect(
                "doctor_register"
            )

        # -------------------------------------------------
        # Create User Account
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # -------------------------------------------------
        # Create Doctor Profile
        # -------------------------------------------------

        DoctorProfile.objects.create(
            user=user,
            name=name,
            qualification=qualification,
            experience=(
                int(experience)
                if experience.isdigit()
                else 0
            ),
            specialization=specialization,
            bio=bio,
            image=image if image else None
        )

        messages.success(
            request,
            "Doctor registration successful! "
            "Please login."
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "doctor_register.html"
    )


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@login_required
def doctor_dashboard(request):

    selected_doctor_id = request.GET.get(
        "doctor_id"
    )

    # =====================================================
    # ADMIN / SUPERUSER
    # =====================================================

    if request.user.is_superuser:

        all_doctors = DoctorProfile.objects.all()

        # Admin selected a specific doctor
        if selected_doctor_id:

            profile = get_object_or_404(
                DoctorProfile,
                id=selected_doctor_id
            )

        # No doctor selected
        else:

            profile = all_doctors.first()

    # =====================================================
    # NORMAL DOCTOR
    # =====================================================

    else:

        all_doctors = None

        profile, created = (
            DoctorProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    "name": (
                        request.user.get_full_name()
                        or request.user.username
                    )
                }
            )
        )

    # =====================================================
    # PROFILE UPDATE
    # =====================================================

    if request.method == "POST":

        if profile is None:

            messages.error(
                request,
                "No doctor profile found to update."
            )

            return redirect(
                "doctor_dashboard"
            )

        # -------------------------------------------------
        # Doctor Name
        # -------------------------------------------------

        profile.name = request.POST.get(
            "name",
            ""
        ).strip()

        # -------------------------------------------------
        # Qualification
        # -------------------------------------------------

        profile.qualification = request.POST.get(
            "qualification",
            ""
        ).strip()

        # -------------------------------------------------
        # Specialization
        # -------------------------------------------------

        profile.specialization = request.POST.get(
            "specialization",
            ""
        ).strip()

        # -------------------------------------------------
        # Bio
        # -------------------------------------------------

        profile.bio = request.POST.get(
            "bio",
            ""
        ).strip()

        # -------------------------------------------------
        # Experience
        # -------------------------------------------------

        experience = request.POST.get(
            "experience",
            ""
        ).strip()

        if experience.isdigit():

            profile.experience = int(
                experience
            )

        else:

            profile.experience = 0

        # -------------------------------------------------
        # Doctor Image
        # -------------------------------------------------

        image = request.FILES.get(
            "image"
        )

        if image:

            profile.image = image

        # -------------------------------------------------
        # Save Profile
        # -------------------------------------------------

        profile.save()

        messages.success(
            request,
            f"Profile updated for Dr. {profile.name}"
        )

        # -------------------------------------------------
        # Admin
        # -------------------------------------------------

        if request.user.is_superuser:

            return redirect(
                f"/doctor/dashboard/?doctor_id={profile.id}"
            )

        # -------------------------------------------------
        # Normal Doctor
        # -------------------------------------------------

        return redirect(
            "doctor_dashboard"
        )

    # =====================================================
    # TEMPLATE CONTEXT
    # =====================================================

    context = {
        "profile": profile,
        "all_doctors": all_doctors,
        "is_admin": request.user.is_superuser,
    }

    return render(
        request,
        "doctor_register.html",
        context
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect(
        "login"
    )


# =========================================================
# HOME / FEEDBACK
# =========================================================

def index(request):

    if (
        request.method == "POST"
        and request.POST.get("form_type") == "feedback"
    ):

        form = FeedbackForm(
            request.POST
        )

        if form.is_valid():

            feedback = form.save()

            # Feedback remains hidden
            # until admin approves it
            feedback.is_approved = False
            feedback.save()

            messages.success(
                request,
                "Thank you for your feedback! "
                "It will be visible after admin approval."
            )

            return redirect(
                "home"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = FeedbackForm()

    # -----------------------------------------------------
    # Only Approved Feedback
    # -----------------------------------------------------

    approved_feedbacks = (
        Feedback.objects
        .filter(
            is_approved=True
        )
        .order_by(
            "-date_created"
        )
    )

    return render(
        request,
        "index.html",
        {
            "feedback_form": form,
            "feedbacks": approved_feedbacks,
        }
    )


# =========================================================
# ABOUT
# =========================================================

def about(request):

    team_members = (
        DoctorProfile.objects
        .filter(
            is_approved=True
        )
    )

    return render(
        request,
        "about.html",
        {
            "team_members": team_members
        }
    )


# =========================================================
# SERVICES
# =========================================================

def services(request):

    return render(
        request,
        "services.html"
    )


# =========================================================
# APPOINTMENT
# =========================================================

def appointment(request):

    if request.method == "POST":

        form = AppointmentForm(
            request.POST
        )

        if form.is_valid():

            # -------------------------------------------------
            # Save Appointment First
            # -------------------------------------------------

            appointment_obj = form.save()

            # -------------------------------------------------
            # Send Emails
            # -------------------------------------------------

            try:

                # =============================================
                # PATIENT EMAIL
                # =============================================

                subject = (
                    f"Appointment Confirmation - "
                    f"{appointment_obj.name}"
                )

                message = f"""
Dear {appointment_obj.name},

Your appointment has been booked successfully.

Appointment Details:

Date: {appointment_obj.date}
Time: {appointment_obj.time}
Service: {appointment_obj.service}
Amount: {
    appointment_obj.amount
    if appointment_obj.amount
    else "To be determined"
}

We will contact you soon for confirmation.

Best regards,
Clinic Team
"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [appointment_obj.email],
                    fail_silently=False,
                )

                # =============================================
                # ADMIN EMAIL
                # =============================================

                admin_subject = (
                    f"New Appointment Booked - "
                    f"{appointment_obj.name}"
                )

                admin_message = f"""
New appointment booked.

Patient Details:

Name: {appointment_obj.name}
Email: {appointment_obj.email}
Phone: {appointment_obj.phone}

Appointment Details:

Date: {appointment_obj.date}
Time: {appointment_obj.time}
Service: {appointment_obj.service}
Amount: {
    appointment_obj.amount
    if appointment_obj.amount
    else "To be determined"
}

Message:
{appointment_obj.message}

Please review and confirm the appointment.
"""

                send_mail(
                    admin_subject,
                    admin_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Appointment booked successfully! "
                    "Confirmation email sent."
                )

            except BadHeaderError:

                messages.warning(
                    request,
                    "Appointment booked, "
                    "but email header was invalid."
                )

            except Exception as e:

                messages.warning(
                    request,
                    "Appointment booked, "
                    "but email notification failed."
                )

            return redirect(
                "appointment_success"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = AppointmentForm()

    return render(
        request,
        "appointment.html",
        {
            "form": form
        }
    )


# =========================================================
# CONTACT
# =========================================================

def contact(request):

    if request.method == "POST":

        form = ContactForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your message has been sent successfully!"
            )

            return redirect(
                "contact"
            )

    else:

        form = ContactForm()

    return render(
        request,
        "contact.html",
        {
            "form": form
        }
    )


# =========================================================
# SUCCESS PAGES
# =========================================================

def appointment_success(request):

    return render(
        request,
        "appointment_success.html"
    )


def contact_success(request):

    return render(
        request,
        "contact_success.html"
    )


def feedback_success(request):

    return render(
        request,
        "feedback_success.html"
    )


# =========================================================
# FEEDBACK UPDATE
# =========================================================

def feedback_update(request, pk):

    feedback = get_object_or_404(
        Feedback,
        pk=pk
    )

    if request.method == "POST":

        form = FeedbackForm(
            request.POST,
            instance=feedback
        )

        if form.is_valid():

            feedback = form.save()

            # Edited feedback requires
            # admin approval again
            feedback.is_approved = False
            feedback.save()

            messages.success(
                request,
                "Feedback updated successfully. "
                "It will be visible after admin approval."
            )

            return redirect(
                "home"
            )

    else:

        form = FeedbackForm(
            instance=feedback
        )

    return render(
        request,
        "feedback_update.html",
        {
            "form": form,
            "feedback": feedback,
        }
    )


# =========================================================
# FEEDBACK DELETE
# =========================================================

def feedback_delete(request, pk):

    feedback = get_object_or_404(
        Feedback,
        pk=pk
    )

    if request.method == "POST":

        feedback.delete()

        messages.success(
            request,
            "Feedback deleted successfully."
        )

    return redirect(
        "home"
    )