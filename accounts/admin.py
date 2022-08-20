from django.contrib import admin

from .models import User, Vendor, Role


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = "phone", "user"
