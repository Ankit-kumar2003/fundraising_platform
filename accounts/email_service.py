from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class EmailService:
    """Abstracts email sending functionality to make it easy to switch email providers."""
    
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None):
        """Send a simple email with the given subject and message."""
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # In a production environment, you would want to log this error
            print(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_template_email(subject, template_name, context, recipient_list):
        """Send an email using a template for both plain text and HTML versions."""
        try:
            # Render plain text message
            text_message = ""
            try:
                text_message = render_to_string(template_name + '.txt', context)
            except Exception:
                # Text template might not exist, that's okay
                pass
            
            # Try to render HTML message if available
            html_message = None
            try:
                html_message = render_to_string(template_name + '.html', context)
            except Exception:
                # HTML template might not exist, that's okay
                pass
            
            return EmailService.send_email(subject, text_message, recipient_list, html_message)
        except Exception as e:
            print(f"Error sending template email: {e}")
            return False
    
    @staticmethod
    def send_verification_email(user, otp):
        """Send a verification email with an OTP code."""
        context = {
            'user': user,
            'otp': otp,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Fundraising Platform',
        }
        
        subject = "Verify your email address"
        template_name = "accounts/email/otp_email"
        
        return EmailService.send_template_email(subject, template_name, context, [user.email])
    
    @staticmethod
    def send_password_reset_email(user):
        """Send a password reset email with a reset link."""
        # Generate UID and token for password reset URL
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        context = {
            'user': user,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Fundraising Platform',
            'protocol': settings.PASSWORD_RESET_PROTOCOL if hasattr(settings, 'PASSWORD_RESET_PROTOCOL') else 'http',
            'domain': settings.PASSWORD_RESET_DOMAIN if hasattr(settings, 'PASSWORD_RESET_DOMAIN') else 'localhost:8000',
            'uid': uid,
            'token': token,
            'expiry_hours': settings.PASSWORD_RESET_TIMEOUT // 3600 if hasattr(settings, 'PASSWORD_RESET_TIMEOUT') else 1
        }
        
        # Use the existing password reset email template
        template_name = 'registration/password_reset_email'
        subject = render_to_string('registration/password_reset_subject.txt', context)
        # Remove any newlines in the subject
        subject = ''.join(subject.splitlines())
        
        return EmailService.send_template_email(subject, template_name, context, [user.email])