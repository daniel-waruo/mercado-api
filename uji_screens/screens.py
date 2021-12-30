from django.template.loader import render_to_string

from orders.models import Order
from products.models import Product
from screens.screens import Screen
from .utils import get_screen


class SelectUjiScreen(Screen):
    state = 'choose_uji'

    def render(self):
        """ returns the list of products to be rendered """
        products = Product.objects.filter(sku__startswith='uji')
        print("prepare the uji products list")
        response = {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Patterns Uji"
                },
                "body": {
                    "text": 'Welcome to Patterns Uji.\nChoose one of our packages .'
                },
                "action": {
                    "button": "Select Patterns Uji",
                    "sections": [
                        {
                            "title": "Select Package",
                            "rows": list(
                                map(
                                    lambda product: {
                                        'id': str(product.id),
                                        'title': product.name,
                                        'description': f"Ksh. {product.price}/kg"
                                    },
                                    products
                                )
                            )
                        },
                    ]
                }
            }
        }
        return response

    def next_screen(self, current_input):
        return get_screen('order_quantity',
                          data={
                              'product_id': int(current_input),
                          })


class OrderQuantityScreen(Screen):
    state = 'order_quantity'
    required_fields = ['product_id']

    def render(self):
        """get the amount of product we should order"""
        product = Product.objects.get(id=self.data['product_id'])
        response = render_to_string(
            'uji/order_quantity.txt',
            context={
                **self.context,
                'errors': self.errors,
                'product': product,
            }
        )
        return response

    def next_screen(self, current_input):
        return get_screen(
            'confirm_order_screen',
            data={
                'product_id': self.data['product_id'],
                'quantity': int(current_input)
            }
        )


class ConfirmOrderScreen(Screen):
    required_fields = ['product_id', 'quantity']
    state = 'confirm_order_screen'

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # get the product to be ordered
        product = Product.objects.get(id=self.data['product_id'])
        # get quantity
        quantity = self.data['quantity']
        body = render_to_string(
            'uji/confirmation_status.txt',
            context={
                'errors': self.errors,
                'product': product,
                'quantity': quantity,
                'total': float(product.price) * float(quantity)
            }
        )
        return {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "Confirm your order"
                },
                "body": {
                    "text": body
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "1",
                                "title": "Yes"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "2",
                                "title": "No"
                            }
                        }
                    ]
                }
            }
        }

    def next_screen(self, current_input):
        print("The user chose " + current_input)
        if current_input == "1":
            return get_screen(
                'finish_order',
                data={
                    'product_id': self.data['product_id'],
                    'quantity': self.data['quantity']
                }
            )
        elif current_input == "2":
            return get_screen('choose_uji')
        else:
            return self.error_screen(errors=["Invalid Input"])


class FinishOrderScreen(Screen):
    required_fields = ['product_id', 'quantity']
    state = 'finish_order'
    type = 'END'

    def render(self):
        product = Product.objects.get(
            id=self.data['product_id']
        )
        # make an order
        order = Order.objects.make_order(
            buyer=self.context['buyer'],
            item=product,
            quantity=self.data['quantity'],
            send_signal=False
        )
        return render_to_string(
            'sms/order_requested.txt',
            context={
                'order': order
            }
        )
