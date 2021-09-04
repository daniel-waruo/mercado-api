from django.conf import settings

from orders.models import Order


def _get_screen(state: str, screen_urls: list, data: dict, errors=None, context: dict = None):
    """searches the screen_urls list and returns the screen"""
    states = [x.state for x in screen_urls]
    if state in states:
        screen_index = states.index(state)
        screen_class = screen_urls[screen_index]
        return screen_class(data, errors, context)
    raise Exception(f"invalid screen url name:{state} not found in urls")


def get_screen(state, data=None, context=None, errors=None, screen_urls=None):
    if screen_urls is None:
        screen_module = __import__(settings.SCREEN_URLS_PATH, globals(), locals(), ['urls'], 0)
        screen_urls = screen_module.screens
    return _get_screen(state=state, screen_urls=screen_urls, data=data, errors=errors, context=context)


def get_last_order_screen(last_product):
    screen = get_screen(
        'last_order',
        data={'product_id': last_product.id}
    )
    return screen


def get_last_ordered_from_order(buyer):
    last_order: Order = Order.objects.filter(buyer=buyer).order_by('id').last()
    if not last_order:
        return last_order
    # get the first order item as for
    # TODO: add tag field to product to allow us to differentiate
    # the refill and cylinder
    return last_order.items.all()[0].product
