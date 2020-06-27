from django.contrib import admin
from .models import Order, OrderItem, OrderMpesaTransaction

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderMpesaTransaction)
