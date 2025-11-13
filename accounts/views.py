from django.shortcuts import render, redirect
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .forms import RegistrationForm, OTPVerificationForm, CustomLoginForm
from .models import CustomUser, OTP
from .email_service import EmailService
from .validators import ACCOUNT_LOCKOUT_ATTEMPTS, ACCOUNT_LOCKOUT_DURATION
from django.shortcuts import redirect

# Set up logger
logger = logging.getLogger(__name__)

# Rate limiting decorators
rate_limit_login = ratelimit(key='ip', rate='10/m', method='POST', block=True)
rate_limit_register = ratelimit(key='ip', rate='5/m', method='POST', block=True)
rate_limit_resend_otp = ratelimit(key='ip', rate='3/m', method='POST', block=True)


@method_decorator(ensure_csrf_cookie, name="dispatch")
@method_decorator(rate_limit_register, name="dispatch")
class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("verify_otp")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Store email and registration timestamp in session
        self.request.session["email"] = user.email
        self.request.session["registration_timestamp"] = timezone.now().isoformat()
        self.request.session.modified = True  # Ensure session is marked as modified
        self.request.session.save()  # Explicitly save the session to ensure data persists

        # Log the registration attempt
        ip_address = self.request.META.get('REMOTE_ADDR')
        logger.info(f"New user registered: {user.email} from IP: {ip_address}")

        # Generate and save OTP with salt
        otp = OTP.generate_otp()
        salt = OTP.generate_salt()
        otp_hash = OTP.hash_otp(otp, salt)
        OTP.objects.create(user=user, otp_hash=otp_hash, salt=salt)

        # Send OTP email with error handling
        try:
            email_sent = EmailService.send_verification_email(user, otp)
            if email_sent:
                logger.info(f"OTP email sent successfully to: {user.email}")
                messages.success(
                    self.request, 
                    "Registration successful! Please check your email for OTP verification. The OTP will expire in 5 minutes."
                )
            else:
                logger.warning(f"Failed to send OTP email to: {user.email}")
                messages.warning(
                    self.request, 
                    "Registration successful, but we couldn't send the verification email. Please try again later."
                )
        except Exception as e:
            # Log the error but continue with the registration process
            logger.error(f"Error sending OTP email to {user.email}: {e}")
            messages.warning(
                self.request, 
                "Registration successful, but we couldn't send the verification email. Please try again later."
            )

        # Directly redirect to verify_otp instead of calling super().form_valid(form)
        return redirect("verify_otp")

    def form_invalid(self, form):
        # Clear any existing session data related to registration
        if "email" in self.request.session:
            del self.request.session["email"]
        if "registration_timestamp" in self.request.session:
            del self.request.session["registration_timestamp"]
        return super().form_invalid(form)


class VerifyOTPView(FormView):
    form_class = OTPVerificationForm
    template_name = "accounts/verify_otp.html"
    success_url = reverse_lazy("login")
    otp_expiry_minutes = 5

    def get(self, request, *args, **kwargs):
        # Check if user came from registration with a valid email in session
        if "email" not in request.session:
            logger.warning("OTP verification attempt without email in session")
            messages.error(request, "Please register first.")
            return redirect("register")
        
        email = request.session.get("email")
        ip_address = request.META.get('REMOTE_ADDR')
        logger.info(f"OTP verification page accessed by email: {email} from IP: {ip_address}")
        
        # Check if registration session has expired
        if "registration_timestamp" in request.session:
            try:
                # Ensure timestamp is properly formatted
                timestamp_str = request.session["registration_timestamp"]
                if isinstance(timestamp_str, str) and timestamp_str:
                    registration_time = timezone.datetime.fromisoformat(timestamp_str)
                    # Ensure datetime is timezone-aware
                    if timezone.is_naive(registration_time):
                        registration_time = timezone.make_aware(registration_time)
                    
                    # Check if session has expired
                    if (timezone.now() - registration_time).total_seconds() > (self.otp_expiry_minutes * 60):
                        logger.warning(f"Verification session expired for email: {email} from IP: {ip_address}")
                        messages.error(request, "Your verification session has expired. Please register again.")
                        # Clear session data
                        self._clear_registration_session()
                        return redirect("register")
                else:
                    raise ValueError("Invalid timestamp format")
            except (ValueError, TypeError) as e:
                logger.error(f"Session timestamp validation error for email: {email}, error: {e}")
                # If timestamp is invalid, clear session and redirect
                self._clear_registration_session()
                messages.error(request, "Invalid session. Please register again.")
                return redirect("register")
        else:
            # If no timestamp in session, add one now to prevent further issues
            request.session["registration_timestamp"] = timezone.now().isoformat()
            request.session.modified = True
            request.session.save()
            logger.info(f"Added missing registration timestamp for email: {email}")
        
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        email = self.request.session.get("email")
        if not email:
            logger.warning("OTP verification attempt with expired session")
            messages.error(self.request, "Session expired. Please register again.")
            return redirect("register")

        ip_address = self.request.META.get('REMOTE_ADDR')
        logger.info(f"OTP verification attempt for email: {email} from IP: {ip_address}")

        try:
            user = CustomUser.objects.get(email=email)
            otp = form.cleaned_data["otp"]

            try:
                otp_obj = OTP.objects.filter(user=user, is_used=False).latest("created_at")
                
                # Check if OTP has expired
                if (timezone.now() - otp_obj.created_at).total_seconds() > (self.otp_expiry_minutes * 60):
                    logger.warning(f"Expired OTP attempt for email: {email} from IP: {ip_address}")
                    messages.error(self.request, "OTP has expired. Please request a new one.")
                    return self.form_invalid(form)
                
                if otp_obj.verify_otp(otp):
                    logger.info(f"Successful OTP verification for email: {email}")
                    user.is_active = True
                    user.save()
                    otp_obj.mark_as_used()
                    
                    # Mark all other OTPs for this user as used
                    OTP.objects.filter(user=user, is_used=False).update(is_used=True)
                    
                    messages.success(
                        self.request, "Email verified successfully! You can now login."
                    )
                    
                    # Clear the registration session data
                    self._clear_registration_session()
                    return super().form_valid(form)
                else:
                    logger.warning(f"Invalid OTP attempt for email: {email} from IP: {ip_address}")
                    messages.error(self.request, "Invalid OTP. Please try again.")
                    return self.form_invalid(form)
            except OTP.DoesNotExist:
                logger.warning(f"No valid OTP found for email: {email} from IP: {ip_address}")
                messages.error(self.request, "No valid OTP found. Please request a new one.")
                return redirect("resend_otp")
        except CustomUser.DoesNotExist:
            logger.warning(f"User not found for email: {email} during OTP verification")
            messages.error(self.request, "User not found.")
            self._clear_registration_session()
            return redirect("register")
    
    def _clear_registration_session(self):
        """Helper method to clear all registration-related session data"""
        email = self.request.session.get("email", "unknown")
        if "email" in self.request.session:
            del self.request.session["email"]
        if "registration_timestamp" in self.request.session:
            del self.request.session["registration_timestamp"]
        logger.info(f"Registration session cleared for email: {email}")


@method_decorator(ensure_csrf_cookie, name="dispatch")
@method_decorator(rate_limit_login, name="dispatch")
class CustomLoginView(FormView):
    form_class = CustomLoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy("features:home")

    def form_valid(self, form):
        email = form.cleaned_data["username"].lower()  # Convert to lowercase
        password = form.cleaned_data["password"]

        try:
            user = CustomUser.objects.get(email=email)

            # Account lockout check
            if hasattr(user, 'failed_login_attempts') and hasattr(user, 'last_failed_login'):
                if user.failed_login_attempts >= ACCOUNT_LOCKOUT_ATTEMPTS:
                    if user.last_failed_login:
                        lockout_duration_seconds = ACCOUNT_LOCKOUT_DURATION
                        lockout_time_left = lockout_duration_seconds - (timezone.now() - user.last_failed_login).total_seconds()
                        if lockout_time_left > 0:
                            lockout_minutes = lockout_duration_seconds // 60
                            lockout_seconds = lockout_time_left % 60
                            messages.error(self.request, 
                                f"Account is locked due to too many failed login attempts. "
                                f"Please try again after {lockout_minutes} minutes and {lockout_seconds} seconds."
                            )
                            return self.form_invalid(form)
                        else:
                            # Reset failed attempts if lockout period has passed
                            user.failed_login_attempts = 0
                            user.save()
                    else:
                        # No last failed login time, reset failed attempts
                        user.failed_login_attempts = 0
                        user.save()

            # Check if user is active
            if not user.is_active:
                logger.info(f"Unverified user attempting to login: {email} from IP: {ip_address}")
                messages.info(self.request, "Your account is not verified yet. Please complete the verification process.")
                # Store email in session and redirect to verification page
                self.request.session["email"] = email
                self.request.session["registration_timestamp"] = timezone.now().isoformat()
                self.request.session.modified = True
                return redirect("verify_otp")

            # Attempt authentication
            user = authenticate(username=email, password=password)
            if user is not None:
                login(self.request, user)
                # Reset failed login attempts
                user.failed_login_attempts = 0
                user.last_failed_login = None
                user.save()
                messages.success(self.request, "Login successful!")
                return redirect(self.get_success_url())
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                user.save()

                remaining_attempts = 5 - user.failed_login_attempts
                if remaining_attempts > 0:
                    messages.error(self.request, f"Invalid password. {remaining_attempts} attempts remaining before account lockout.")
                else:
                    messages.error(self.request, "Account locked for 5 minutes due to too many failed attempts.")
                return self.form_invalid(form)

        except CustomUser.DoesNotExist:
            messages.error(self.request, "No account found with this email address. Please check the email or register for a new account.")
            return self.form_invalid(form)



@rate_limit_resend_otp
def resend_otp(request):
    if request.method == "POST":
        # First check for email in POST data (from login page verification option), then fall back to session
        email = request.POST.get("email") or request.session.get("email")
        registration_timestamp = request.session.get("registration_timestamp")
        ip_address = request.META.get('REMOTE_ADDR')
        
        logger.info(f"OTP resend attempt from IP: {ip_address}")
        
        if not email:
            logger.warning(f"OTP resend attempt without email in session or POST data from IP: {ip_address}")
            messages.error(request, "No email found. Please register again.")
            return redirect("register")
        
        # If email came from POST (login page) and not session, store it in session
        if request.POST.get("email") and not request.session.get("email"):
            request.session["email"] = email
            request.session["registration_timestamp"] = timezone.now().isoformat()
            request.session.modified = True
            logger.info(f"Added email to session from POST request: {email}")
        
        # Verify registration session hasn't expired
        if registration_timestamp:
            try:
                timestamp = timezone.datetime.fromisoformat(registration_timestamp)
                if timezone.is_naive(timestamp):
                    timestamp = timezone.make_aware(timestamp)
                
                # Set a reasonable session expiration period (e.g., 1 hour)
                if (timezone.now() - timestamp).total_seconds() > 3600:
                    logger.warning(f"Registration session expired for email: {email} from IP: {ip_address}")
                    messages.error(request, "Your registration session has expired. Please register again.")
                    # Clear expired session data
                    for key in ['email', 'registration_timestamp']:
                        if key in request.session:
                            del request.session[key]
                    request.session.modified = True
                    return redirect("register")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid session timestamp for email: {email}, error: {e}")
                messages.error(request, "Invalid session data. Please register again.")
                return redirect("register")
        
        try:
            user = CustomUser.objects.get(email=email)
            logger.info(f"OTP resend attempt for email: {email} from IP: {ip_address}")
            
            # Check for existing non-expired OTPs to prevent unnecessary resends
            latest_otp = OTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
            if latest_otp and not latest_otp.is_expired():
                # Calculate remaining time before another OTP can be sent
                time_since_creation = (timezone.now() - latest_otp.created_at).total_seconds()
                cooldown_period = 60  # 1 minute cooldown
                if time_since_creation < cooldown_period:
                    remaining_seconds = int(cooldown_period - time_since_creation)
                    logger.info(f"OTP resend cooldown active for email: {email}, remaining: {remaining_seconds}s")
                    messages.info(
                        request, 
                        f"Please wait {remaining_seconds} seconds before requesting another OTP."
                    )
                    # Redirect with cooldown in hash to activate frontend countdown
                return redirect(reverse("verify_otp") + f"#cooldown={remaining_seconds}")
            
            # Generate and send new OTP
            otp = OTP.generate_otp()
            salt = OTP.generate_salt()
            otp_hash = OTP.hash_otp(otp, salt)
            OTP.objects.create(user=user, otp_hash=otp_hash, salt=salt)

            # Use the EmailService to send OTP email
            email_sent = EmailService.send_verification_email(user, otp)
            if email_sent:
                logger.info(f"OTP successfully resent to email: {email}")
                messages.success(request, _('New OTP has been sent to your email address. Please check your inbox.'))
                # Redirect with cooldown in hash to activate frontend countdown
                return redirect(reverse("verify_otp") + "#cooldown=60")
            else:
                logger.warning(f"Failed to send OTP email to: {email}")
                messages.warning(request, "We couldn't send the verification email. Please try again later.")
        except CustomUser.DoesNotExist:
            logger.warning(f"User not found for email: {email} during OTP resend attempt")
            messages.error(request, "User not found.")
            return redirect("register")
    
    # Update the registration timestamp to extend the session
    request.session["registration_timestamp"] = timezone.now().isoformat()
    request.session.modified = True
    return redirect("verify_otp")
