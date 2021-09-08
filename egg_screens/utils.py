from egg_screens.screen_urls import get_screens
from screens.utils import get_screen as _get_screen
from orders.models import Order


def get_screen(state, data=None, context=None, errors=None):
    return _get_screen(state=state, screen_urls=get_screens(), data=data, errors=errors, context=context)


def get_last_ordered_from_order(buyer):
    last_order: Order = Order.objects.filter(buyer=buyer).order_by('id').last()
    if not last_order:
        return last_order
    # get the first order item as for
    # TODO: add tag field to product to allow us to differentiate
    # the refill and cylinder
    return last_order.items.all()[0].product
