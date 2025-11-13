from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from .validators import ACCOUNT_LOCKOUT_ATTEMPTS, ACCOUNT_LOCKOUT_DURATION

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch the user by email (case-insensitive)
            user = UserModel.objects.get(email__iexact=username)
            
            # Check if account is locked
            if hasattr(user, 'failed_login_attempts') and hasattr(user, 'last_failed_login'):
                if user.failed_login_attempts >= ACCOUNT_LOCKOUT_ATTEMPTS:
                    if user.last_failed_login:
                        lockout_time_left = ACCOUNT_LOCKOUT_DURATION - (timezone.now() - user.last_failed_login).total_seconds()
                        if lockout_time_left > 0:
                            # Account is still locked
                            return None
                        else:
                            # Lockout period has passed, reset failed attempts
                            user.failed_login_attempts = 0
                            user.save()
                    else:
                        # No last failed login time, reset failed attempts
                        user.failed_login_attempts = 0
                        user.save()
            
            if user.check_password(password):
                # Successful login, reset failed attempts if they exist
                if hasattr(user, 'failed_login_attempts') and user.failed_login_attempts > 0:
                    user.failed_login_attempts = 0
                    user.save()
                return user
            else:
                # Failed login, increment attempts if attribute exists
                if hasattr(user, 'failed_login_attempts'):
                    user.failed_login_attempts += 1
                    user.last_failed_login = timezone.now()
                    user.save()
                return None
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user.
            UserModel().set_password(password)
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None