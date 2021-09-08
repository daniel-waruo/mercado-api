from .models import Buyer


def get_buyer(phone_number):
    buyer, created = Buyer.objects.get_or_create(phone_number=phone_number)
    # TODO:create a buyer created signal
    return buyer
