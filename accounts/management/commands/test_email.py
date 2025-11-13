from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Send a test email to verify SMTP configuration'

    def handle(self, *args, **kwargs):
        try:
            # Get email settings from environment
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = settings.EMAIL_HOST_USER  # Send to the same email for testing
            subject = 'Test Email - Fundraising Platform'
            message = 'This is a test email to verify that the SMTP configuration is working properly.'
            
            self.stdout.write(f'Sending test email from {from_email} to {to_email}')
            self.stdout.write(f'Using SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
            
            # Send the email
            send_mail(
                subject,
                message,
                from_email,
                [to_email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS('Successfully sent test email!'))
            self.stdout.write(self.style.NOTICE('Please check your email inbox (and spam folder) for the test message.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {str(e)}'))
            self.stdout.write(self.style.ERROR('Check your SMTP settings in the .env file and ensure your Gmail account is properly configured.'))
            self.stdout.write(self.style.NOTICE('For Gmail, make sure you have enabled "Less secure app access" or generated an "App password" if you have 2-factor authentication enabled.'))