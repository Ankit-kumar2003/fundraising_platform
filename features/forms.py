from django import forms
from .models import Campaign, Donation, DonorProfile, Expense


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            "title",
            "description",
            "target_amount",
            "start_date",
            "end_date",
            "image",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class DonationForm(forms.ModelForm):
    VISIBILITY_CHOICES = [
        (False, "Donate Silently (Anonymous)"),
        (True, "Donate Publicly"),
    ]
    donate_publicly = forms.ChoiceField(
        choices=VISIBILITY_CHOICES,
        widget=forms.RadioSelect,
        label="Donation Visibility",
    )

    class Meta:
        model = Donation
        fields = ["amount", "payment_method", "donate_publicly"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Set the anonymous field based on the user's choice
        instance.anonymous = not bool(int(self.cleaned_data["donate_publicly"]))
        if commit:
            instance.save()
        return instance

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Donation amount must be greater than zero.")
        return amount


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ["phone_number", "address", "pan_number", "photo"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "description", "amount", "date", "receipt"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Expense amount must be greater than zero.")
        return amount
