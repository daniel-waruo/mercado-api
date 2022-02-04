from products.models import Product
from screens.screens import Screen
from shop.utils import get_screen
from whatsapp.parsers import parse

class ShopMenu(Screen):
    state = 'shop_menu'

    def render(self):
        """ return category of products to be rendered """
        response = {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Patterns Store"
                },
                "body": {
                    "text": 'Welcome to Patterns Store'
                },
                "action": {
                    "button": "Select Product",
                    "sections": [
                        {
                            "title": "Select Product",
                            "rows": [
                                {
                                    'id': 'menu:eggs',
                                    'title': 'Eggs (tray)',
                                    'description': 'Get the freshest eggs in town.'
                                },
                                {
                                    'id': 'menu:gas',
                                    'title': 'Gas',
                                    'description': 'Get the best gas deals.'
                                },
                                {
                                    'id': 'menu:uji',
                                    'title': 'Porridge',
                                    'description': 'Healthy and nutritious.'
                                }
                            ]
                        },
                    ]
                }
            }
        }
        return response

    def next_screen(self, current_input):
        category = parse(current_input, 'interactive').split(':')[1]
        return get_screen('get_cereals', data={'category': category})


class CerealsScreen(Screen):
    state = 'get_cereals'
    required_fields = ['category']

    def render(self):
        """ returns the list of products to be rendered """
        products = Product.objects.filter(sku__icontains=self.data['category'])
        response = {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {
                    "type": "text",
                    "text": "Select Product"
                },
                "body": {
                    "type": "text",
                    "text": "Get the highest quality cereals"
                },
                "action": {
                    "catalog_id": "886770702008655",
                    "sections": [
                        {
                            "product_items": list(map(
                                lambda product: {
                                    "product_retailer_id": product.sku
                                },
                                products
                            ))
                        }
                    ]
                }
            }
        }
        return response
