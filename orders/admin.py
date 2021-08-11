from django.contrib import admin

from buyers.models import Buyer
from .models import Order, OrderItem
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from django.utils.safestring import mark_safe


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    def has_change_permission(self, *args, **kwargs):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'buyer_link', 'status', 'created_at')
    inlines = [
        OrderItemInline
    ]

    def buyer_link(self, obj):
        url = resolve_url(admin_urlname(Buyer._meta, 'change'), obj.buyer.id)
        return mark_safe(
            f'<a href="{url}">{str(obj.buyer)}</a>'
        )

    buyer_link.short_description = 'buyer'
