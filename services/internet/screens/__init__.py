from django.template.loader import render_to_string

from payments.stk import initiate_stk
from screens.screens import Screen
from services.utils import get_screen
from whatsapp.parsers import parse
from whatsapp.utils import send_whatsapp


class SelectProviderScreen(Screen):
    state = 'internet_menu'

    def render(self):
        """ return category of products to be rendered """
        buyer = self.context["buyer"]
        providers = [
            {
                'id': 1,
                'name': 'Elite Technologies',
            },
            {
                'id': 2,
                'name': 'Safaricom Internet',
            },
            {
                'id': 'add',
                'name': 'Add Another',
            }
        ]
        text = f"Hi {buyer.name} , \n Select Internet Provider"
        return {
            "recipient_type": "individual",
            "to": buyer.phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Select Internet Provider"
                },
                "body": {
                    "text": text
                },
                "action": {
                    "button": "Select Provider",
                    "sections": [
                        {
                            "title": "Select Internet Provider",
                            "rows": list(map(
                                lambda provider: {
                                    'id': f'{provider["id"]}',
                                    'title': f'{provider["name"]}',
                                },
                                providers
                            ))
                        },
                    ]
                }
            }
        }

    def next_screen(self, current_input):
        text = parse(current_input, 'interactive')
        if text == "add":
            return get_screen('add_internet_provider')
        return get_screen('provider_package')


class AddProviderScreen(Screen):
    state = 'add_internet_provider'

    def render(self):
        return render_to_string('internet/add_provider.txt', context={"errors": self.errors})

    def next_screen(self, current_input):
        text = parse(current_input, "text")
        phone_number = self.context['buyer'].phone
        if text == "WRONG":
            return self.error_screen(errors=["Invalid Input"])
        send_whatsapp(phone_number, "Successfully Added Provider")
        return get_screen('internet_menu')


class SelectProviderPackageScreen(Screen):
    state = 'provider_package'

    def render(self):
        """ return category of products to be rendered """
        buyer = self.context["buyer"]
        providers = [
            {
                'id': 1,
                'name': ' Elite 2.5MB/s ',
                'price': "Ksh. 3000"
            },
            {
                'id': 2,
                'name': ' Elite 5.0MB/s ',
                'price': "Ksh. 5000"
            },
        ]
        text = f"Hi {buyer.name} , \n Select Payment Package"
        return {
            "recipient_type": "individual",
            "to": buyer.phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Elite Internet"
                },
                "body": {
                    "text": text
                },
                "action": {
                    "button": "Select Package",
                    "sections": [
                        {
                            "title": "Select Payment Package",
                            "rows": list(map(
                                lambda provider: {
                                    'id': f'{provider["id"]}',
                                    'title': f'{provider["name"]}',
                                    'description': f'{provider["price"]}',
                                },
                                providers
                            ))
                        },
                    ]
                }
            }
        }

    def next_screen(self, current_input):
        return get_screen('pay_internet')


class PayInternetScreen(Screen):
    state = 'pay_internet'

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
        phone_number = self.context['buyer'].phone
        if text == "1":
            send_whatsapp(
                phone_number,
                'Please wait to Enter M-Pesa Pin On your Phone',
            )
            is_success, transaction = initiate_stk(
                phone_number,
                1,
                'https://makinika.com',
                'TEST'
            )
            return get_screen(
                'payment_pending',
                data={'success': is_success}
            )
        elif text == "2":
            return get_screen('internet_get_phone')
        else:
            return self.error_screen(errors=["Invalid Input"])


class GetInternetPhoneScreen(Screen):
    state = 'internet_get_phone'

    def render(self):
        return 'Send us your phone number format 07xxxxxx .'

    def next_screen(self, current_input):
        phone_number = parse(current_input, "text")
        send_whatsapp(
            self.context['buyer'].phone,
            'Please wait to Enter M-Pesa Pin On your Phone',
        )
        is_success, transaction = initiate_stk(
            f"254{phone_number[0:]}",
            1,
            'https://makinika.com',
            'TEST'
        )
        return get_screen(
            'internet_payment_pending',
            data={
                'success': is_success
            })


class InternetPaymentPendingScreen(Screen):
    required_fields = ['is_success']
    state = 'internet_payment_pending'

    def render(self):
        is_success = self.data['is_success']
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
            return get_screen('pay_internet')
        if text == "2":
            return get_screen('internet_menu')
