from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTP


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "full_name", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("email", "full_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Security", {"fields": ("failed_login_attempts", "last_failed_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password1", "password2"),
            },
        ),
    )


class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "user__full_name")
    ordering = ("-created_at",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
