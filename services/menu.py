import sys
import traceback

from screens.screens import Screen
from services.utils import get_screen


class MainMenu(Screen):
    state = 'main_menu'

    def render(self):
        buyer = self.context['buyer']
        text = f"""
            Hi 👋 {buyer.name} ,\n How can we help you today ?.
        """
        return {
            "to": buyer.phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "Select Service"
                },
                "body": {
                    "text": text
                },
                "action": {
                    "button": "Select Service",
                    "sections": [
                        {
                            "title": "Select Service",
                            "rows": [
                                {
                                    'id': f'main_menu:shop',
                                    'title': 'Retail Store',
                                    'description': 'Get cereals,rice , maize flour and GAS REFILL'
                                },
                                {
                                    'id': f'main_menu:internet',
                                    'title': 'Pay for Internet',
                                    'description': 'Pay for your internet subscription.'
                                },
                                {
                                    'id': f'main_menu:hotels',
                                    'title': 'Order Food',
                                    'description': 'Order from your favourite restaurants.'
                                }
                            ]
                        },
                    ]
                }
            }
        }

    def next_screen(self, current_input: str):
        try:
            current_input = current_input.split(':')[1]
            return get_screen(f'{current_input}_menu')
        except Exception as e:
            print("-" * 60)
            print(e)
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)
            return get_screen('main_menu', data=self.data)
