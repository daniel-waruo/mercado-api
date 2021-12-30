from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
from django.utils import timezone

from buyers.models import Buyer
from whatsapp.utils import send_whatsapp


def months(start: timezone.datetime, end: timezone.datetime):
    result = []
    while start <= end:
        result.append(start)
        start += relativedelta(months=1)
    return result


def send_notification(buyer: Buyer, title, text):
    message = render_to_string(
        'sms/notification.txt',
        context={
            'buyer': buyer,
            'notification': text,
            'title': title.upper()
        }
    )
    send_whatsapp(
        to=buyer.phone,
        message=message
    )
