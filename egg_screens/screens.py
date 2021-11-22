from django.template.loader import render_to_string

from orders.models import Order
from products.models import Product
from screens.screens import Screen as BaseScreen
from .utils import get_screen


class Screen(BaseScreen):
    type = 'CON'

    def render_ussd(self):
        return f"{self.type} {self.render()}"


class OrderQuantityScreen(Screen):
    state = 'order_quantity'
    type = 'CON'

    def render(self):
        """return choose egg menu screen"""
        product = Product.objects.get(sku='eggs')
        # choose products under brand and send it to the template
        response = render_to_string(
            'egg/order_quantity.txt',
            context={
                **self.context,
                'errors': self.errors,
                'product': product,
            }
        )
        return response

    def next_screen(self, current_input: int):
        """shows ownership status of the screen"""
        # check for errors in ownership and go to the next step
        # which is ownership status
        try:
            product = Product.objects.get(sku='eggs')
        except (Product.DoesNotExist, IndexError):
            return self.error_screen(errors=['Invalid option.Check and try again'])
        return get_screen('confirm_order_screen',
                          data={
                              'product_id': product.id,
                              'quantity': current_input
                          })


class ConfirmOrderScreen(Screen):
    required_fields = ['product_id', 'quantity']
    state = 'confirm_order_screen'
    context = None
    type = 'CON'

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # check if the user has valid input
        product = Product.objects.get(id=self.data['product_id'])
        # get quantity
        quantity = self.data['quantity']
        return render_to_string(
            'egg/confirmation_status.txt',
            context={
                'errors': self.errors,
                'product': product,
                'quantity': quantity,
                'total': product.price * quantity
            }
        )

    def next_screen(self, current_input):
        if current_input not in [1, 2]:
            return self.error_screen(errors=["Invalid Input"])
        if current_input == 1:
            return get_screen(
                'finish_order',
                data={
                    'product_id': self.data['product_id'],
                    'quantity': self.data['quantity']
                }
            )
        if current_input == 2:
            return get_screen('order_quantity')


class FinishOrderScreen(Screen):
    required_fields = ['product_id', 'quantity']
    state = 'finish_order'
    type = 'END'

    def render(self):
        product = Product.objects.get(
            id=self.data['product_id']
        )
        # make an order
        Order.objects.make_order(
            buyer=self.context['buyer'],
            item=product,
            quantity=self.data['quantity']
        )
        return render_to_string(
            'egg/finish_order.txt',
            context={
                'errors': self.errors,
                'product': product
            }
        )
