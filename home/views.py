from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Appointment, Contact, Feedback, DoctorProfile
from .forms import AppointmentForm, ContactForm, FeedbackForm


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin / Boss
            if user.is_superuser:
                return redirect("/admin/")

            # Doctor
            return redirect("doctor_dashboard")

        else:

            return render(
                request,
                "login.html",
                {
                    "error": "Invalid username or password."
                }
            )

    return render(request, "login.html")


# =========================================================
# DOCTOR REGISTER
# =========================================================

# =========================================================
# DOCTOR REGISTER
# =========================================================


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import DoctorProfile

def doctor_register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        
        name = request.POST.get("name", "").strip()
        qualification = request.POST.get("qualification", "").strip()
        experience = request.POST.get("experience", "").strip()
        specialization = request.POST.get("specialization", "").strip()
        bio = request.POST.get("bio", "").strip()
        image = request.FILES.get("image")

        # 1. User account create karein
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("doctor_register")

        user = User.objects.create_user(username=username, email=email, password=password)

        # 2. DoctorProfile create karein
        profile = DoctorProfile.objects.create(
            user=user,
            name=name,
            qualification=qualification,
            experience=int(experience) if experience.isdigit() else 0,
            specialization=specialization,
            bio=bio,
            image=image if image else None
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "doctor_register.html")

# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@login_required
def doctor_dashboard(request):

    selected_doctor_id = request.GET.get("doctor_id")

    # =====================================================
    # ADMIN / SUPERUSER
    # =====================================================

    if request.user.is_superuser:

        all_doctors = DoctorProfile.objects.all()

        if selected_doctor_id:
            profile = get_object_or_404(
                DoctorProfile,
                id=selected_doctor_id
            )
        else:
            profile = all_doctors.first()

    # =====================================================
    # NORMAL DOCTOR
    # =====================================================

    else:

        all_doctors = None

        profile, created = DoctorProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "name": request.user.get_full_name()
                or request.user.username
            }
        )

    # =====================================================
    # PROFILE UPDATE
    # =====================================================

    if request.method == "POST":

        if not profile:

            messages.error(
                request,
                "No doctor profile found to update."
            )

            return redirect("doctor_dashboard")

        profile.name = request.POST.get(
            "name",
            ""
        ).strip()

        profile.qualification = request.POST.get(
            "qualification",
            ""
        ).strip()

        profile.specialization = request.POST.get(
            "specialization",
            ""
        ).strip()

        profile.bio = request.POST.get(
            "bio",
            ""
        ).strip()

        experience = request.POST.get(
            "experience",
            ""
        ).strip()

        profile.experience = (
            int(experience)
            if experience.isdigit()
            else 0
        )

        image = request.FILES.get("image")

        if image:
            profile.image = image

        profile.save()

        messages.success(
            request,
            f"Profile updated for Dr. {profile.name}"
        )

        # Admin selected doctor ko wahi rakho
        if request.user.is_superuser:

            return redirect(
                f"/doctor/dashboard/?doctor_id={profile.id}"
            )

        # Normal doctor
        return redirect("doctor_dashboard")

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
        "doctor_register",
        context
    )

# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================================
# HOME / FEEDBACK
# =========================================================

def index(request):

    if request.method == "POST" and request.POST.get("form_type") == "feedback":

        form = FeedbackForm(request.POST)

        if form.is_valid():

            form.save()
            messages.success(
                request,
                "Thank you for your feedback!"
            )

            return redirect("home")

        else:

            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = FeedbackForm()

    return render(
        request,
        "index.html",
        {
            "feedback_form": form
        }
    )


# =========================================================
# ABOUT
# =========================================================

from django.shortcuts import render
from .models import DoctorProfile

def about(request):
    team_members = DoctorProfile.objects.filter(is_approved=True)
    return render(request, 'about.html', {'team_members': team_members})

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
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # 1. Save directly to the database first
            appointment = form.save()

            # 2. Attempt to send emails after saving
            try:
                subject = f"Appointment Confirmation - {appointment.name}"
                message = f"""
Dear {appointment.name},

Your appointment has been booked successfully.

Details:
Date: {appointment.date}
Time: {appointment.time}
Service: {appointment.service}
Amount: {appointment.amount or 'To be determined'}

We will contact you soon for confirmation.

Best regards,
Clinic Team
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [appointment.email],
                    fail_silently=False,
                )

                admin_subject = f"New Appointment Booked - {appointment.name}"
                admin_message = f"""
New appointment booked:

Name: {appointment.name}
Email: {appointment.email}
Phone: {appointment.phone}
Date: {appointment.date}
Time: {appointment.time}
Service: {appointment.service}
Amount: {appointment.amount or 'To be determined'}
Message: {appointment.message}

Please review and confirm.
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
                    "Appointment booked successfully! Confirmation email sent."
                )

            except BadHeaderError:
                messages.warning(
                    request,
                    "Appointment booked, but email header was invalid."
                )
            except Exception as e:
                messages.warning(
                    request,
                    f"Appointment booked, but email notification failed: {str(e)}"
                )

            return redirect("appointment_success")

        else:
            messages.error(
                request,
                "Please correct the errors below."
            )
    else:
        form = AppointmentForm()

    return render(
        request,
        "appointment.html",
        {"form": form}
    )


# =========================================================
# CONTACT
# =========================================================

def contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your message has been sent successfully!"
            )

            return redirect("contact")

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