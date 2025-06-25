from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, OTP


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit OTP"}),
    )


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "autofocus": True}),
        error_messages={
            "invalid": "Please enter a valid email address.",
            "required": "Please enter your email address.",
        },
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        error_messages={
            "required": "Please enter your password.",
        },
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            email = email.lower()  # Convert email to lowercase
            self.cleaned_data["username"] = email

            # Check if user exists and is active
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_active:
                    raise forms.ValidationError(
                        "Please verify your email first.",
                        code="inactive",
                    )
            except CustomUser.DoesNotExist:
                pass

        return super().clean()
