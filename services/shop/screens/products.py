import json

from screens.screens import Screen
from services.shop.utils import fetch_products, get_category


class CategoryProducts(Screen):
    state = 'category_products'

    required_fields = ['category_id']

    def render(self):
        """ return category of products to be rendered """
        category_id = self.data['category_id']
        category = get_category(category_id)
        products = fetch_products(category=category_id)
        print(json.dumps(products, indent=2))
        return {
            "recipient_type": "individual",
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {
                    "type": "text",
                    "text": f"{category['name']}"
                },
                "body": {
                    "text": category["description"] or category["name"]
                },
                "action": {
                    "catalog_id": "886770702008655",
                    "sections": [
                        {
                            "title": category["name"],
                            "product_items": list(map(
                                lambda product: {
                                    "product_retailer_id": f"{product['sku']}_{product['id']}"
                                },
                                products
                            ))
                        }
                    ]
                }
            }
        }
