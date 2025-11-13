from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .custom_auth_views import password_reset_view
from django.views.generic import TemplateView
from django.urls import reverse_lazy


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("features:home")),
        name="logout",
    ),
    # Password Reset URLs
    path(
        "password-reset/",
        password_reset_view,
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("", TemplateView.as_view(template_name="accounts/home.html"), name="home"),
]
