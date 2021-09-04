from django.urls import path
from .views import order_mpesa_callback

urlpatterns = [
    path('order', order_mpesa_callback),
]
