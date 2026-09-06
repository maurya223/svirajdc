

from . import views
from django.urls import path
from . import views

urlpatterns = [

    # HOME
    path(
        "",
        views.index,
        name="home"
    ),

    # ABOUT
    path(
        "about/",
        views.about,
        name="about"
    ),

    # SERVICES
    path(
        "services/",
        views.services,
        name="services"
    ),

    # APPOINTMENT
    path(
        "appointment/",
        views.appointment,
        name="appointment"
    ),

    path(
        "appointment/success/",
        views.appointment_success,
        name="appointment_success"
    ),

    # CONTACT
    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "contact/success/",
        views.contact_success,
        name="contact_success"
    ),
    # LOGIN
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    # DOCTOR REGISTER
    path(
        "doctor/register/",
        views.doctor_register,
        name="doctor_register"
    ),

    # DOCTOR DASHBOARD
    path(
        "doctor/dashboard/",
        views.doctor_dashboard,
        name="doctor_dashboard"
    ),

    # LOGOUT
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]