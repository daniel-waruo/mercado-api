from .models import Buyer
from asgiref.sync import sync_to_async, async_to_sync


def get_buyer(phone_number):
    buyer, created = Buyer.objects.get_or_create(phone_number=phone_number)
    # TODO:create a buyer created signal
    return buyer


get_buyer_async = sync_to_async(get_buyer,thread_sensitive=True)
