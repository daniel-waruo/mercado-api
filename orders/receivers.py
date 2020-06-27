from time import sleep
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.template.loader import render_to_string

from buyers.models import ContactQueue
from dj_africastalking.pay import pay
from dj_africastalking.sms import send_sms
from ussd_screens.signals import request_finished
from .models import OrderCheckout
from .signals import (
    checkout_request,
    order_delivered,
    order_cancel,
    order_shipping,
    order_requested,
    payment_fail,
    payment_success
)


@receiver(checkout_request)
def make_checkout_request(sender, **kwargs):
    OrderCheckout.objects.create(
        order=kwargs['order']
    )


@receiver(request_finished)
def mobile_checkout(sender, **kwargs):
    session = kwargs['session']
    buyer = session.context['buyer']
    session_state = session.session.state
    if session_state == 'finish_mpesa' and OrderCheckout.objects.filter(order__buyer=buyer).exists():
        order_checkout = OrderCheckout.objects.filter(order__buyer=buyer).last()
        OrderCheckout.objects.filter(order__buyer=buyer).delete()
        order = order_checkout.order
        product_name = settings.AFRICASTALKING['product_name']
        total_amount = float(order.get_order_total())
        """sleep for 5 sec to ensure the user has called the dialog"""
        sleep(5)
        pay.mobile_checkout(
            product_name=product_name,
            phone_number=order.buyer.phone_number,
            currency_code='KES',
            amount=total_amount,
            metadata={
                'order_id': str(order.id)
            }
        )


@receiver(order_requested)
def send_order_notification_to_vendor(sender, **kwargs):
    order = kwargs["order"]
    buyer = order.buyer
    reason = """
        GET LOCATION 
        FROM BUYER:{}
        ITEM :{}
    """.format(buyer.phone_number, order.items)
    ContactQueue.objects.add(buyer, reason=reason)


@receiver(order_requested)
def send_order_notification_to_buyer(sender, **kwargs):
    order = kwargs["order"]
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/order_requested.txt',
            context={
                'buyer': order.buyer,
                'order': order,
            }
        )
    )


@receiver(order_shipping)
def send_order_shipping_to_buyer(sender, **kwargs):
    order = kwargs['order']
    delivery_start = timezone.datetime.now() + timezone.timedelta(minutes=30)
    delivery_end = timezone.datetime.now() + timezone.timedelta(hours=1)
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/order_shipping.txt',
            context={
                'buyer': order.buyer,
                'order': order,
                'delivery_start': delivery_start,
                'delivery_end': delivery_end
            }
        )
    )


@receiver(order_cancel)
def send_order_cancelled_notification(sender, **kwargs):
    order = kwargs['order']
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/order_cancel.txt',
            context={
                'buyer': order.buyer,
                'order': order,
            }
        )
    )
    reason = """
        CANCELLED ORDER REASON
        FROM_BUYER : {}
        ITEM : {}
        AMOUNT : KES {}
    """.format(
        order.buyer.phone_number,
        order.items,
        order.get_order_total()
    )
    ContactQueue.objects.add(order.buyer, reason=reason)


@receiver(payment_success)
def send_payment_success_notification(sender, **kwargs):
    order = kwargs['order']
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/payment_success.txt',
            context={
                'buyer': order.buyer,
                'order': order
            }
        )
    )
    reason = """
        PAYMENT SUCCESS EXPERIENCE
        FROM_BUYER : {}
        ITEM : {}
        AMOUNT : KES {}
    """.format(
        order.buyer.phone_number,
        order.items,
        order.get_order_total()
    )
    ContactQueue.objects.add(order.buyer, reason=reason)


@receiver(payment_fail)
def send_payment_failed_notification(sender, **kwargs):
    order = kwargs['order']
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/payment_failure.txt',
            context={
                'buyer': order.buyer,
                'order': order
            }
        )
    )
    reason = """
        PAYMENT FAILURE INQUIRY
        FROM_BUYER : {}
        ITEM : {}
        AMOUNT : KES {}
    """.format(
        order.buyer.phone_number,
        order.items,
        order.get_order_total()
    )
    ContactQueue.objects.add(order.buyer, reason=reason)


@receiver(order_delivered)
def send_delivered_success_notification(sender, **kwargs):
    order = kwargs['order']
    send_sms(
        order.buyer.phone_number,
        render_to_string(
            'sms/payment_success.txt',
            context={
                'buyer': order.buyer,
                'order': order
            }
        )
    )
    reason = """
        DELIVERY SUCCESS EXPERIENCE
        FROM_BUYER : {}
        ITEM : {}
        AMOUNT : KES {}
        PAYMENT METHOD : {}
    """.format(
        order.buyer.phone_number,
        order.items,
        order.get_order_total(),
        order.payment_method
    )
    ContactQueue.objects.add(order.buyer, reason=reason)
