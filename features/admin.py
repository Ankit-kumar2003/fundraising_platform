from django.contrib import admin
from .models import Campaign, Donation, DonorProfile, Expense

# Register your models here.
admin.site.register(Campaign)
admin.site.register(Donation)
admin.site.register(DonorProfile)
admin.site.register(Expense)
