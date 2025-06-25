from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, OTP

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

    def test_otp_hashing(self):
        otp = "123456"
        hashed = OTP.hash_otp(otp)
        self.assertEqual(len(hashed), 64)  # SHA-256 produces 64 characters
        self.assertNotEqual(otp, hashed)

    def test_otp_verification(self):
        otp = "123456"
        otp_obj = OTP.objects.create(user=self.user, otp_hash=OTP.hash_otp(otp))

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

    def test_mark_as_used(self):
        otp = "123456"
        otp_obj = OTP.objects.create(user=self.user, otp_hash=OTP.hash_otp(otp))

        self.assertFalse(otp_obj.is_used)
        otp_obj.mark_as_used()
        self.assertTrue(otp_obj.is_used)
