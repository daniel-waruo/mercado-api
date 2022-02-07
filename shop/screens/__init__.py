from products.models import Category
from screens.screens import Screen


class ShopMenu(Screen):
    state = 'shop_menu'

    def render(self):
        """ return category of products to be rendered """
        categories = Category.objects.all()
        responses = []
        for category in categories:
            products = category.products.filter(active=True)
            if len(products):
                responses.append({
                    "recipient_type": "individual",
                    "type": "interactive",
                    "interactive": {
                        "type": "product_list",
                        "header": {
                            "type": "text",
                            "text": f"Shop for {category.name}"
                        },
                        "body": {
                            "type": "text",
                            "text": f"Shop for {category.name}"
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
                })
        return responses

