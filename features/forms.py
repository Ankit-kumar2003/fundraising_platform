from django import forms
from .models import Campaign, Donation, DonorProfile, Expense, DonorReport
from django.utils import timezone
from datetime import date, timedelta
import mimetypes


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
    class Meta:
        model = Donation
        fields = ["amount", "payment_method"]

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
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class DonorReportForm(forms.ModelForm):
    """Form for generating donor contribution reports"""
    
    class Meta:
        model = DonorReport
        fields = ['campaign', 'export_format', 'date_from', 'date_to']
        widgets = {
            'campaign': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'export_format': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'date_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'date_to': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show campaigns where the user has made donations
        if user:
            donated_campaigns = Campaign.objects.filter(
                donation__donor=user
            ).distinct().order_by('title')
            self.fields['campaign'].queryset = donated_campaigns
        
        # Set default date range to last 12 months
        today = date.today()
        one_year_ago = today - timedelta(days=365)
        self.fields['date_from'].initial = one_year_ago
        self.fields['date_to'].initial = today
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise forms.ValidationError("Start date must be before end date.")
            
            # Limit date range to prevent excessive data
            if (date_to - date_from).days > 1095:  # 3 years
                raise forms.ValidationError("Date range cannot exceed 3 years.")
        
        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=150, required=True)
    category = forms.ChoiceField(
        choices=[
            ("support", "Support"),
            ("donation", "Donation"),
            ("campaign", "Campaign"),
            ("feedback", "Feedback"),
            ("other", "Other"),
        ],
        required=False,
    )
    message = forms.CharField(widget=forms.Textarea, max_length=2000, required=True)
    attachment = forms.FileField(required=False)
    captcha = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        self.expected_captcha = kwargs.pop("expected_captcha", None)
        super().__init__(*args, **kwargs)
        # Add basic CSS classes to widgets for consistency with existing styles
        self.fields["name"].widget.attrs.update({"class": "form-control", "placeholder": "Your full name"})
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Your email address"})
        self.fields["subject"].widget.attrs.update({"class": "form-control", "placeholder": "Subject"})
        self.fields["category"].widget.attrs.update({"class": "form-control"})
        self.fields["message"].widget.attrs.update({"class": "form-control", "rows": 4, "placeholder": "Describe your query or issue in detail"})
        self.fields["attachment"].widget.attrs.update({"class": "form-control", "accept": ".png,.jpg,.jpeg,.pdf"})
        self.fields["captcha"].widget.attrs.update({"class": "form-control", "inputmode": "numeric", "placeholder": "Answer"})

    def clean_attachment(self):
        file = self.cleaned_data.get("attachment")
        if not file:
            return file
        # Validate file size (max 5 MB, and not empty)
        max_size = 5 * 1024 * 1024
        size = getattr(file, "size", 0)
        if size == 0 or size > max_size:
            raise forms.ValidationError("File size must be between 1B and 5MB.")
        # Validate content type or extension
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        allowed_exts = {".jpg", ".jpeg", ".png", ".pdf"}
        name = getattr(file, "name", "")
        content_type = getattr(file, "content_type", None)
        guessed_type, _ = mimetypes.guess_type(name)
        if content_type not in allowed_types:
            # Fallback to extension/MIME guess validation
            ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
            if f".{ext}" not in allowed_exts and (guessed_type not in allowed_types):
                raise forms.ValidationError("Unsupported file type. Allowed: JPG, PNG, PDF.")
        return file

    def clean_captcha(self):
        value = self.cleaned_data.get("captcha")
        if self.expected_captcha is None or value != self.expected_captcha:
            raise forms.ValidationError("CAPTCHA verification failed. Please try again.")
        return value
