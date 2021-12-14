from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Vendor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = "phone", "user"
