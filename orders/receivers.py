from django.conf import settings
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import Vendor
from dj_africastalking.sms import send_sms
from whatsapp.utils import send_whatsapp
from .signals import (
    order_delivered,
    order_cancel,
    order_shipping,
    order_requested,
    payment_fail,
    payment_success,
    payment_pending
)

vendor_phone = settings.VENDOR["phone"]


@receiver(order_requested, dispatch_uid="vendor_order_notification")
def send_order_notification_to_vendor(sender, **kwargs):
    order = kwargs["order"]
    message = render_to_string(
        'sms/order_notification.txt',
        context={
            'buyer': order.buyer,
            'order': order,
        }
    )
    vendors = Vendor.objects.all()
    for vendor in vendors:
        send_whatsapp(
            to=f'{vendor.phone}',
            message=message
        )


@receiver(order_requested, dispatch_uid="buyer_order_notification")
def send_order_notification_to_buyer(sender, **kwargs):
    order = kwargs["order"]
    channel = kwargs["channel"]
    store_name = 'Daniel'
    store_phone = '254797792447'
    if kwargs.get('store'):
        store = kwargs['store']
        store_name = store.name
        store_phone = store.phone
    message = render_to_string(
        'sms/order_requested.txt',
        context={
            'buyer': order.buyer,
            'order': order,
            'store_name': store_name,
            'store_phone': store_phone
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(order_shipping)
def send_order_shipping_to_buyer(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    delivery_start = timezone.now() + timezone.timedelta(minutes=30)
    delivery_end = timezone.now() + timezone.timedelta(hours=1)
    message = render_to_string(
        'sms/order_shipping.txt',
        context={
            'buyer': order.buyer,
            'order': order,
            'delivery_start': delivery_start,
            'delivery_end': delivery_end
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(order_cancel)
def send_order_cancelled_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    message = render_to_string(
        'sms/order_cancel.txt',
        context={
            'buyer': order.buyer,
            'order': order,
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(order_delivered)
def send_delivered_success_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    message = render_to_string(
        'sms/order_delivered.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(payment_pending)
def send_payment_success_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    message = render_to_string(
        'sms/payment_success.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(payment_success)
def send_payment_success_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    message = render_to_string(
        'sms/payment_success.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )


@receiver(payment_fail)
def send_payment_failed_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs.get("channel", "whatsapp")
    message = render_to_string(
        'sms/payment_failure.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone, message)
    else:
        send_whatsapp(
            to=order.buyer.phone,
            message=message
        )
