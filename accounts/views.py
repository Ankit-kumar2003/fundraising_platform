from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import CreateView, FormView, TemplateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .forms import RegistrationForm, OTPVerificationForm, CustomLoginForm
from .models import CustomUser, OTP
from django.contrib.auth.decorators import login_required


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("verify_otp")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Store email in session
        self.request.session["email"] = user.email

        # Generate and save OTP
        otp = OTP.generate_otp()
        OTP.objects.create(user=user, otp_hash=OTP.hash_otp(otp))

        # Send OTP email
        context = {"user": user, "otp": otp}
        html_message = render_to_string("accounts/email/otp_email.html", context)
        send_mail(
            "Verify your email",
            f"Your OTP is: {otp}",
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Registration successful! Please check your email for OTP verification.",
        )
        return super().form_valid(form)


class VerifyOTPView(FormView):
    form_class = OTPVerificationForm
    template_name = "accounts/verify_otp.html"
    success_url = reverse_lazy("login")

    def get(self, request, *args, **kwargs):
        if "email" not in request.session:
            messages.error(request, "Please register first.")
            return redirect("register")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        email = self.request.session.get("email")
        if not email:
            messages.error(self.request, "Session expired. Please register again.")
            return redirect("register")

        try:
            user = CustomUser.objects.get(email=email)
            otp = form.cleaned_data["otp"]

            try:
                otp_obj = OTP.objects.filter(user=user, is_used=False).latest(
                    "created_at"
                )
                if otp_obj.verify_otp(otp):
                    user.is_active = True
                    user.save()
                    otp_obj.mark_as_used()
                    messages.success(
                        self.request, "Email verified successfully! You can now login."
                    )
                    # Clear the email from session
                    del self.request.session["email"]
                    return super().form_valid(form)
                else:
                    messages.error(self.request, "Invalid or expired OTP.")
                    return self.form_invalid(form)
            except OTP.DoesNotExist:
                messages.error(self.request, "No valid OTP found.")
                return self.form_invalid(form)
        except CustomUser.DoesNotExist:
            messages.error(self.request, "User not found.")
            return redirect("register")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CustomLoginView(FormView):
    form_class = CustomLoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("features:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        
        email = form.cleaned_data["username"].lower()  # Convert to lowercase
        password = form.cleaned_data["password"]
        
        logger.debug(f"Login attempt for email: {email}")

        try:
            user = CustomUser.objects.get(email=email)
            logger.debug(f"User found: {user.email}, is_active: {user.is_active}")

            # Check if user is active
            if not user.is_active:
                logger.debug(f"User {email} is not active")
                messages.error(self.request, "Please verify your email first.")
                return self.form_invalid(form)

            # Check for account lockout
            if user.failed_login_attempts >= 5:
                lockout_duration = 300  # 5 minutes in seconds
                logger.debug(f"User {email} has {user.failed_login_attempts} failed attempts")
                if (
                    user.last_failed_login
                    and (timezone.now() - user.last_failed_login).total_seconds()
                    < lockout_duration
                ):
                    remaining_time = int(
                        lockout_duration
                        - (timezone.now() - user.last_failed_login).total_seconds()
                    )
                    messages.error(
                        self.request,
                        f"Account is locked. Please try again after {remaining_time} seconds.",
                    )
                    return self.form_invalid(form)
                else:
                    # Reset failed attempts if lockout period has passed
                    user.failed_login_attempts = 0
                    user.save()
                    logger.debug(f"Reset failed attempts for user {email}")

            # Attempt authentication
            logger.debug(f"Attempting to authenticate user {email}")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(self.request, user)
                logger.debug(f"Authentication successful for user {email}")
                # Reset failed login attempts
                user.failed_login_attempts = 0
                user.last_failed_login = None
                logger.debug(f"Redirecting to success_url: {self.get_success_url()}")
                user.save()
                messages.success(self.request, "Login successful!")
                return super().form_valid(form)
            else:
                logger.debug(f"Authentication failed for user {email}")
                # Increment failed login attempts
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                user.save()
                logger.debug(f"Incremented failed attempts for user {email}, now at {user.failed_login_attempts}")

                remaining_attempts = 5 - user.failed_login_attempts
                if remaining_attempts > 0:
                    messages.error(
                        self.request,
                        f"Invalid password. {remaining_attempts} attempts remaining before account lockout.",
                    )
                else:
                    messages.error(
                        self.request,
                        "Account locked for 5 minutes due to too many failed attempts.",
                    )
                return self.form_invalid(form)

        except CustomUser.DoesNotExist:
            messages.error(self.request, "No account found with this email address.")
            return self.form_invalid(form)


def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                otp = OTP.generate_otp()
                OTP.objects.create(user=user, otp_hash=OTP.hash_otp(otp))

                context = {"user": user, "otp": otp}
                html_message = render_to_string(
                    "accounts/email/otp_email.html", context
                )
                send_mail(
                    "Verify your email",
                    f"Your OTP is: {otp}",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, "New OTP has been sent to your email.")
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("register")
        else:
            messages.error(request, "No email found in session.")
            return redirect("register")
    return redirect("verify_otp")
