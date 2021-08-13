from django.utils import timezone
from django.dispatch import receiver
from django.template.loader import render_to_string
from dj_africastalking.sms import send_sms
from whatsapp.utils import send_whatsapp
from .signals import (
    order_delivered,
    order_cancel,
    order_shipping,
    order_requested,
    payment_fail,
    payment_success
)
from django.conf import settings

vendor_phone = settings.VENDOR["phone"]
vendor_whatsapp = settings.VENDOR["whatsapp_phone"]


@receiver(order_requested)
def send_order_notification_to_vendor(sender, **kwargs):
    order = kwargs["order"]
    buyer = order.buyer
    if not buyer.location:
        message = render_to_string(
            'sms/notification.txt',
            context={
                'buyer': order.buyer,
                'order': order,
                'notification': 'Get Buyer Location'
            }
        )
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{vendor_phone}',
            message=message
        )


@receiver(order_requested)
def send_order_notification_to_vendor(sender, **kwargs):
    order = kwargs["order"]
    message = render_to_string(
        'sms/order_notification.txt',
        context={
            'buyer': order.buyer,
            'order': order,
        }
    )
    send_whatsapp(
        from_=f'whatsapp:{vendor_whatsapp}',
        to_=f'whatsapp:{vendor_phone}',
        message=message
    )


@receiver(order_requested)
def send_order_notification_to_buyer(sender, **kwargs):
    order = kwargs["order"]
    channel = kwargs["channel"]
    message = render_to_string(
        'sms/order_requested.txt',
        context={
            'buyer': order.buyer,
            'order': order,
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )


@receiver(order_shipping)
def send_order_shipping_to_buyer(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs["channel"]
    delivery_start = timezone.datetime.now() + timezone.timedelta(minutes=30)
    delivery_end = timezone.datetime.now() + timezone.timedelta(hours=1)
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
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )


@receiver(order_cancel)
def send_order_cancelled_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs["channel"]
    message = render_to_string(
        'sms/order_cancel.txt',
        context={
            'buyer': order.buyer,
            'order': order,
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )


@receiver(order_delivered)
def send_delivered_success_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs["channel"]
    message = render_to_string(
        'sms/order_delivered.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )


@receiver(payment_success)
def send_payment_success_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs["channel"]
    message = render_to_string(
        'sms/payment_success.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )


@receiver(payment_fail)
def send_payment_failed_notification(sender, **kwargs):
    order = kwargs['order']
    channel = kwargs["channel"]
    message = render_to_string(
        'sms/payment_failure.txt',
        context={
            'buyer': order.buyer,
            'order': order
        }
    )
    if channel == "ussd" or channel == "sms":
        send_sms(order.buyer.phone_number, message)
    else:
        send_whatsapp(
            from_=f'whatsapp:{vendor_whatsapp}',
            to_=f'whatsapp:{order.buyer.phone_number}',
            message=message
        )
