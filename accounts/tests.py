from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, OTP
from django.urls import reverse
from django.contrib.auth import get_user_model

# Create your tests here.


class OTPModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com", full_name="Test User", password="testpass123"
        )

    def test_otp_generation(self):
        otp = OTP.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_salt_generation(self):
        salt = OTP.generate_salt()
        self.assertEqual(len(salt), 32)  # 16 bytes hex encoded

    def test_otp_hashing(self):
        otp = "123456"
        salt = OTP.generate_salt()
        hashed = OTP.hash_otp(otp, salt)
        self.assertEqual(len(hashed), 64)  # SHA-256 produces 64 characters
        self.assertNotEqual(otp, hashed)
        # Verify the same OTP with same salt produces same hash
        self.assertEqual(hashed, OTP.hash_otp(otp, salt))
        # Verify the same OTP with different salt produces different hash
        self.assertNotEqual(hashed, OTP.hash_otp(otp, OTP.generate_salt()))

    def test_otp_verification(self):
        otp = "123456"
        salt = OTP.generate_salt()
        otp_obj = OTP.objects.create(user=self.user, otp_hash=OTP.hash_otp(otp, salt), salt=salt)

        # Test valid OTP
        self.assertTrue(otp_obj.verify_otp(otp))

        # Test invalid OTP
        self.assertFalse(otp_obj.verify_otp("000000"))

        # Test expired OTP
        otp_obj.created_at = timezone.now() - timedelta(minutes=6)
        otp_obj.save()
        self.assertFalse(otp_obj.verify_otp(otp))

        # Test used OTP
        otp_obj.created_at = timezone.now()
        otp_obj.is_used = True
        otp_obj.save()
        self.assertFalse(otp_obj.verify_otp(otp))

    def test_is_expired(self):
        otp = "123456"
        salt = OTP.generate_salt()
        otp_obj = OTP.objects.create(user=self.user, otp_hash=OTP.hash_otp(otp, salt), salt=salt)
        
        # Test not expired
        self.assertFalse(otp_obj.is_expired())
        
        # Test expired
        otp_obj.created_at = timezone.now() - timedelta(minutes=6)
        otp_obj.save()
        self.assertTrue(otp_obj.is_expired())

    def test_mark_as_used(self):
        otp = "123456"
        salt = OTP.generate_salt()
        otp_obj = OTP.objects.create(user=self.user, otp_hash=OTP.hash_otp(otp, salt), salt=salt)

        self.assertFalse(otp_obj.is_used)
        otp_obj.mark_as_used()
        self.assertTrue(otp_obj.is_used)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.verify_otp_url = reverse('verify_otp')
        self.login_url = reverse('login')
        self.resend_otp_url = reverse('resend_otp')
        self.logout_url = reverse('logout')
        
        # Create a verified user for login tests
        self.verified_user = CustomUser.objects.create_user(
            email="verified@example.com", 
            full_name="Verified User", 
            password="testpass123"
        )
        self.verified_user.is_active = True
        self.verified_user.save()

    def test_registration_form_valid(self):
        # Check if user exists before registration
        self.assertFalse(CustomUser.objects.filter(email='newuser@example.com').exists())
        
        response = self.client.post(self.register_url, {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'Testpass123!',
            'confirm_password': 'Testpass123!'
        })
        
        # Check redirect to OTP verification page
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.verify_otp_url, response.url)
        
        # Check user exists but is inactive
        user = CustomUser.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)
        
        # Check if OTP was generated for the user
        self.assertTrue(OTP.objects.filter(user=user).exists())

    def test_registration_form_invalid(self):
        response = self.client.post(self.register_url, {
            'email': 'invalid-email',
            'full_name': 'Invalid User',
            'password': 'test',
            'confirm_password': 'different'
        })
        
        # Form should be invalid and not redirect
        self.assertEqual(response.status_code, 200)
        
        # Check if form is in context and has errors
        form = response.context['form']
        self.assertTrue(form.errors)
        
        # Check specific field errors
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
        
        # Verify no user was created
        self.assertFalse(CustomUser.objects.filter(email='invalid-email').exists())

    def test_login_valid(self):
        response = self.client.post(self.login_url, {
            'username': 'verified@example.com',
            'password': 'testpass123'
        })
        
        # Check redirect to home page
        self.assertRedirects(response, reverse('features:home'))
        
        # Check user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid(self):
        response = self.client.post(self.login_url, {
            'username': 'verified@example.com',
            'password': 'wrongpassword'
        })
        
        # Form should be invalid and not redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_inactive_user(self):
        # Create an inactive user
        inactive_user = CustomUser.objects.create_user(
            email="inactive@example.com", 
            full_name="Inactive User", 
            password="testpass123"
        )
        inactive_user.is_active = False
        inactive_user.save()
        
        response = self.client.post(self.login_url, {
            'username': 'inactive@example.com',
            'password': 'testpass123'
        })
        
        # Form should be invalid and not redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
