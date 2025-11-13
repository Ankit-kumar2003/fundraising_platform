from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils import timezone

# Function-based view for password reset with rate limiting
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def password_reset_view(request, *args, **kwargs):
    # Check if this is a POST request and has an email
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        if email:
            from .models import CustomUser
            import logging
            logger = logging.getLogger(__name__)
            ip_address = request.META.get('REMOTE_ADDR')
            
            try:
                # Check if user exists and is verified
                user = CustomUser.objects.get(email=email)
                if not user.is_active:
                    logger.info(f"Unverified user attempting to reset password: {email} from IP: {ip_address}")
                    from django.contrib import messages
                    from django.shortcuts import redirect
                    messages.info(request, "Your account is not verified yet. Please complete the verification process first.")
                    # Store email in session and redirect to verification page
                    request.session["email"] = email
                    request.session["registration_timestamp"] = timezone.now().isoformat()
                    request.session.modified = True
                    return redirect("verify_otp")
            except CustomUser.DoesNotExist:
                # User doesn't exist, let the standard view handle it
                pass
    
    # Create an instance of the standard PasswordResetView
    view = auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done'),
        from_email="noreply@fundraisingplatform.com",
        extra_email_context={
            'domain': settings.PASSWORD_RESET_DOMAIN,
            'protocol': settings.PASSWORD_RESET_PROTOCOL
        }
    )
    return view(request, *args, **kwargs)