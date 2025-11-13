import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')

# Import Django modules
import django
django.setup()

from django.conf import settings
from accounts.email_service import EmailService

# Simple user mock - we'll patch the token generator directly
user_mock = MagicMock()
user_mock.email = 'test@example.com'
user_mock.username = 'testuser'
user_mock.pk = 1

# Test settings
settings.PASSWORD_RESET_DOMAIN = '127.0.0.1:8000'
settings.PASSWORD_RESET_PROTOCOL = 'http'
settings.SITE_NAME = 'Fundraising Platform'
settings.PASSWORD_RESET_TIMEOUT = 3600  # 1 hour
settings.DEFAULT_FROM_EMAIL = 'admin@fundraisingplatform.com'

def test_email_service():
    """Test that EmailService correctly uses PASSWORD_RESET_DOMAIN and PASSWORD_RESET_PROTOCOL settings."""
    print("\nTesting EmailService...\n")
    
    # Patch send_mail where it's imported in the EmailService module
    with patch('accounts.email_service.send_mail') as mock_send_mail, \
         patch('accounts.email_service.default_token_generator') as mock_token_generator, \
         patch('accounts.email_service.urlsafe_base64_encode') as mock_base64_encode:
        
        # Configure mocks
        mock_send_mail.return_value = 1
        mock_token_generator.make_token.return_value = 'mock-token-123'
        mock_base64_encode.return_value = b'mock-uid-123'
        
        # Test verification email
        print("Testing verification email:")
        otp = '123456'
        result = EmailService.send_verification_email(user_mock, otp)
        print(f"Verification email result: {result}")
        assert result is True, "Verification email should be sent successfully"
        
        # Check if the mock was called
        print(f"Mock send_mail called: {mock_send_mail.called}")
        assert mock_send_mail.called, "send_mail should be called"
        
        # Get the arguments passed to send_mail
        args, kwargs = mock_send_mail.call_args
        print(f"send_mail args: {args}")
        print(f"send_mail kwargs: {kwargs}")
        
        # Reset the mock for the next test
        mock_send_mail.reset_mock()
        
        # Test password reset email
        print("Testing password reset email:")
        # Note: We don't need to pass reset_url anymore since the method generates it internally
        result = EmailService.send_password_reset_email(user_mock)
        print(f"Password reset email result: {result}")
        assert result is True, "Password reset email should be sent successfully"
        
        # Check if the mock was called
        print(f"Mock send_mail called: {mock_send_mail.called}")
        assert mock_send_mail.called, "send_mail should be called"
        
        # Get the arguments passed to send_mail
        args, kwargs = mock_send_mail.call_args
        print(f"send_mail args: {args}")
        print(f"send_mail kwargs: {kwargs}")
        
        # Verify that PASSWORD_RESET_DOMAIN and PASSWORD_RESET_PROTOCOL are used
        email_content = kwargs.get('message', '')
        html_content = kwargs.get('html_message', '')
        
        # Check that at least one of email_content or html_content is not None and contains the domain and protocol
        content_has_domain = (email_content and settings.PASSWORD_RESET_DOMAIN in email_content) or \
                            (html_content and settings.PASSWORD_RESET_DOMAIN in html_content)
        content_has_protocol = (email_content and settings.PASSWORD_RESET_PROTOCOL in email_content) or \
                              (html_content and settings.PASSWORD_RESET_PROTOCOL in html_content)
        
        assert content_has_domain, f"{settings.PASSWORD_RESET_DOMAIN} should be in the email content"
        assert content_has_protocol, f"{settings.PASSWORD_RESET_PROTOCOL} should be in the email content"
        
    print("\nAll tests passed successfully!")

if __name__ == '__main__':
    test_email_service()