from django.http import HttpResponseRedirect
from django.urls import reverse
from django_ratelimit.exceptions import Ratelimited
from django.contrib import messages

class RateLimitExceededMiddleware:
    """Middleware to handle rate limiting exceptions and display user-friendly error messages."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Ratelimited:
            # Check which view the user was trying to access
            path = request.path
            
            # Determine appropriate error message and redirect URL based on the path
            if 'login' in path:
                message = "You've made too many login attempts. Please try again later."
                redirect_url = reverse('login')
            elif 'register' in path:
                message = "You've made too many registration attempts. Please try again later."
                redirect_url = reverse('register')
            elif 'resend_otp' in path:
                message = "You've requested too many OTP resends. Please try again later."
                redirect_url = reverse('verify_otp')
            elif 'password_reset' in path:
                message = "You've made too many password reset requests. Please try again later."
                redirect_url = reverse('password_reset')
            else:
                message = "You've made too many requests. Please try again later."
                redirect_url = reverse('features:home')
                
            # Add message and redirect
            messages.error(request, message)
            return HttpResponseRedirect(redirect_url)
            
        return response