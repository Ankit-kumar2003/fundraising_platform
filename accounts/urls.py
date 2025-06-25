from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


class LogoutGetView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path(
        "logout/",
        LogoutGetView.as_view(next_page=reverse_lazy("features:home")),
        name="logout",
    ),
    # path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Password Reset URLs
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
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
