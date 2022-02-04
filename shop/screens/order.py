from django.template.loader import render_to_string

from orders.models import Order
from payments.models import OrderTransaction
from payments.utils import pay_for_order
from products.models import Product
from screens.screens import Screen
from shop.utils import get_screen
from whatsapp.parsers import parse
from whatsapp.utils import send_whatsapp


class GetLocationScreen(Screen):
    required_fields = ['order']
    state = 'get_location'

    def render(self):
        return render_to_string('shop/get_location.txt')

    def next_screen(self, current_input):
        location = current_input.get('location', {
            'longitude': -1.23432,
            'latitude': 21.4232323
        })
        return get_screen(
            'payment_method',
            data={
                "order": self.data["order"],
                "location": location
            }
        )


class PaymentMethodScreen(Screen):
    required_fields = ['order', 'location']
    state = 'payment_method'

    def render(self):
        """ returns a confirmation status screen if ownership else finished  """
        # get quantity
        body = render_to_string(
            'shop/payment_method.txt',
        )
        return {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "Select Payment Method"
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
                                "title": "M pesa"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "2",
                                "title": "On Delivery"
                            }
                        }
                    ]
                }
            }
        }

    def next_screen(self, current_input):
        text = parse(current_input, "button")
        assert text in ["1", "2"]
        order = Order.objects.create(
            payment_method="m-pesa" if text == "1" else "on-delivery",
            buyer=self.context['buyer'],
            longitude=self.data['location']['longitude'],
            latitude=self.data['location']['latitude']
        )
        for product_item in self.data["order"]["product_items"]:
            item = Product.objects.get(
                sku=product_item["product_retailer_id"]
            )
            quantity = product_item["quantity"]
            # add item to order
            order.add_item(item, quantity)

        if text == "1":
            return get_screen(
                'pay_order',
                data={
                    'order_id': order.id,
                }
            )
        if text == "2":
            return get_screen(
                'finish_order',
                data={
                    'order_id': order.id
                }
            )


class FinishOrderScreen(Screen):
    required_fields = ['order_id']
    state = 'finish_order'

    def render(self):
        order = Order.objects.get(id=self.data['order_id'])
        return render_to_string(
            'sms/order_requested.txt',
            context={
                'order': order
            }
        )


class PayOrderScreen(Screen):
    required_fields = ['order_id']
    state = 'pay_order'

    def render(self):
        body = render_to_string(
            'shop/payment_phone.txt',
            context={
                'phone': self.context['buyer'].phone
            }
        )
        return {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "Select Payment Phone"
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
        text = parse(current_input, "button")
        if text == "1":
            order = Order.objects.get(id=self.data['order_id'])
            send_whatsapp(
                self.context['buyer'].phone,
                'Please wait to Enter M-Pesa Pin On your Phone',
            )
            is_success, transaction = pay_for_order(order, phone=self.context['buyer'].phone)
            transaction: OrderTransaction = transaction
            return get_screen(
                'payment_pending',
                data={
                    'success': is_success,
                    'order_id': transaction.order.id
                })
        elif text == "2":
            return get_screen(
                'get_phone',
                data={
                    'order_id': self.data['order_id']
                }
            )
        else:
            return self.error_screen(errors=["Invalid Input"])


class GetPhoneScreen(Screen):
    required_fields = ['order_id']
    state = 'get_phone'

    def render(self):
        return 'Send us your phone number format 07xxxxxx .'

    def next_screen(self, current_input):
        phone_number = parse(current_input, "text")
        order = Order.objects.get(id=self.data['order_id'])
        send_whatsapp(
            self.context['buyer'].phone,
            'Please wait to Enter M-Pesa Pin On your Phone',
        )
        is_success, transaction = pay_for_order(order, phone=phone_number)
        transaction: OrderTransaction = transaction
        return get_screen(
            'payment_pending',
            data={
                'success': is_success,
                'order_id': transaction.order.id
            })


class PaymentPendingScreen(Screen):
    state = 'payment_pending'
    required_fields = ['success', 'order_id']

    def render(self):
        is_success = self.data['success']
        if is_success:
            return "...awaiting payment"
        body = render_to_string('sms/payment_failure.txt')
        return {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "Payment Failed"
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
        text = parse(current_input, 'text')
        if text == "1":
            return get_screen(
                'pay_order',
                data={
                    'order_id': self.data["order_id"],
                }
            )
        if text == "2":
            return get_screen(
                'finish_order',
                data={
                    'order_id': self.data["order_id"]
                }
            )
