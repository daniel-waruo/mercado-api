from . import africastalking
from django.conf import settings

pay = africastalking.Payment


def test_pay():
    return pay.mobile_checkout(
        product_name=settings.AFRICASTALKING['product_name'],
        phone_number="+254797792447",
        currency_code='KES',
        amount=300.0,
        metadata={
            'order_id': 'Test ID'
        }
    )
