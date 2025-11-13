from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    """Custom password validator to enforce stronger password requirements."""
    
    def validate(self, password, user=None):
        """Validate that the password meets complexity requirements."""
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "Your password must contain at least one uppercase letter.",
                code='password_no_uppercase',
            )
            
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "Your password must contain at least one lowercase letter.",
                code='password_no_lowercase',
            )
            
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "Your password must contain at least one special character.",
                code='password_no_special',
            )
    
    def get_help_text(self):
        """Return a help text explaining the password requirements."""
        return "Your password must contain at least 8 characters, including uppercase and lowercase letters, and a special character."


# Account lockout settings
ACCOUNT_LOCKOUT_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION = 300  # 5 minutes in seconds