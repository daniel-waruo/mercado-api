from django.contrib import admin

from .models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    fields = ('name', 'phone_number', 'location')
    list_display = ('__str__', 'phone_number', 'location')
