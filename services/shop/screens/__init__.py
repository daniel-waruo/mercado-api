from django.template.loader import render_to_string

from screens.screens import Screen
from services.shop.utils import fetch_categories
from services.utils import get_screen
from whatsapp.parsers import parse


class ShopMenu(Screen):
    state = 'shop_menu'

    def render(self):
        """ return category of products to be rendered """
        buyer = self.context['buyer']
        # fetch woo categories
        categories = fetch_categories()
        text = render_to_string('shop/welcome.txt')
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": buyer.phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Wakini.co"
                },
                "body": {
                    "text": text
                },
                "action": {
                    "button": "Select Category",
                    "sections": [
                        {
                            "title": "Categories",
                            "rows": list(
                                map(
                                    lambda category: (
                                        {
                                            "id": category["id"],
                                            "title": category["name"],
                                            "description": category["description"]
                                        }
                                    ),
                                    categories
                                )
                            )
                        }
                    ]
                }
            }
        }

    def next_screen(self, current_input):
        return get_screen(
            'category_products',
            data={
                'category_id': parse(current_input, 'interactive')
            }
        )
