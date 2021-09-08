from django.contrib import admin

from buyers.models import Buyer
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from django.utils.safestring import mark_safe

from orders.models import Order
from store.models import StoreProduct, Store, StoreOrder


class StoreProductInline(admin.TabularInline):
    model = StoreProduct


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'phone', 'code')
    inlines = [
        StoreProductInline
    ]


@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'buyer_link', 'order_status', 'order_created_at')

    def order_link(self, obj: StoreOrder):
        url = resolve_url(admin_urlname(Order._meta, 'change'), obj.order.id)
        return mark_safe(
            f'<a href="{url}">{str(obj.order)}</a>'
        )

    order_link.short_description = 'order'

    def buyer_link(self, obj: StoreOrder):
        url = resolve_url(admin_urlname(Buyer._meta, 'change'), obj.order.buyer.id)
        return mark_safe(
            f'<a href="{url}">{str(obj.order.buyer)}</a>'
        )

    buyer_link.short_description = 'buyer'

    def order_created_at(self, obj: StoreOrder):
        return obj.order.status

    order_created_at.short_description = 'created_at'

    def order_status(self, obj: StoreOrder):
        return obj.order.status

    order_status.short_description = 'status'
