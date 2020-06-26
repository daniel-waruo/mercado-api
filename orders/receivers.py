from time import sleep

from django.conf import settings
from django.dispatch import receiver
from dj_africastalking.pay import pay
from ussd_screens.signals import request_finished
from .models import OrderCheckout
from .signals import checkout_request
from django.utils.termcolors import colorize


@receiver(checkout_request)
def make_checkout_request(sender, **kwargs):
    OrderCheckout.objects.create(
        order=sender
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
