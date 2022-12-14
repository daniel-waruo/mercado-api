import inspect

from orders.models import Order
from screens.screens import Screen
from screens.utils import get_screen as _get_screen


def get_screens():
    from .screen_urls import screens
    screen_urls = []
    for key, value in screens.items():
        if inspect.isclass(value):
            if issubclass(value, Screen) and not value == Screen:
                screen_urls.append(value)
    return screen_urls


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
