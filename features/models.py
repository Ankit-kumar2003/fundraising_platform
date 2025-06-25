from django.db import models
from django.conf import settings
from django.utils import timezone


class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="campaign_images/", null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return (self.collected_amount / self.target_amount) * 100
        return 0


class Donation(models.Model):
    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("BANK_TRANSFER", "Bank Transfer"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    donation_date = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.donor.full_name} - ₹{self.amount} - {self.campaign.title}"


class DonorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    total_donations = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_donation_date = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)

    def __str__(self):
        return self.user.full_name


class Expense(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    receipt = models.FileField(upload_to="expense_receipts/", null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
