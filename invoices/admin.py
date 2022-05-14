from django.contrib import admin
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.shortcuts import resolve_url
from django.utils.safestring import mark_safe

from buyers.models import Buyer
from .models import InvoiceItem, Invoice


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem

    def has_change_permission(self, *args, **kwargs):
        return False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'buyer_link', 'status', 'created_at')
    inlines = [
        InvoiceItemInline
    ]

    def buyer_link(self, obj):
        url = resolve_url(admin_urlname(Buyer._meta, 'change'), obj.buyer.id)
        return mark_safe(
            f'<a href="{url}">{str(obj.buyer)}</a>'
        )

    buyer_link.short_description = 'buyer'
