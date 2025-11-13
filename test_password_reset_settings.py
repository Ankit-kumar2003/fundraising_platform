import os
import sys
from django.conf import settings
from django.core.management import execute_from_command_line

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_system.settings')

# Configure Django
execute_from_command_line(['manage.py', 'check'])

# Test password reset settings
def test_password_reset_settings():
    """Test that PASSWORD_RESET_DOMAIN and PASSWORD_RESET_PROTOCOL are correctly set based on DEBUG mode."""
    
    print("Testing password reset settings...")
    print(f"DEBUG mode: {settings.DEBUG}")
    print(f"PASSWORD_RESET_DOMAIN: {settings.PASSWORD_RESET_DOMAIN}")
    print(f"PASSWORD_RESET_PROTOCOL: {settings.PASSWORD_RESET_PROTOCOL}")
    
    # Verify settings are correct based on DEBUG mode
    if settings.DEBUG:
        assert settings.PASSWORD_RESET_DOMAIN in ['127.0.0.1:8000', 'localhost:8000'], \
            f"Expected development domain, got {settings.PASSWORD_RESET_DOMAIN}"
        assert settings.PASSWORD_RESET_PROTOCOL == 'http', \
            f"Expected 'http' protocol in development, got {settings.PASSWORD_RESET_PROTOCOL}"
    else:
        assert settings.PASSWORD_RESET_DOMAIN != '127.0.0.1:8000', \
            f"Production should not use development domain"
        assert settings.PASSWORD_RESET_PROTOCOL == 'https', \
            f"Expected 'https' protocol in production, got {settings.PASSWORD_RESET_PROTOCOL}"
    
    print("Password reset settings test passed!")

if __name__ == '__main__':
    test_password_reset_settings()