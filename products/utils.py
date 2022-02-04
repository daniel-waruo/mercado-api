import requests

from products.models import Product


def update_facebook_catalog(product: Product, catalog_id, access_token, operation='UPDATE', body=None):
    url = f"https://graph.facebook.com/v12.0/{catalog_id}/batch"
    payload = {
        'access_token': access_token,
        'requests': [
            {
                'method': operation,
                'retailer_id': product.sku,
                'data': body or {

                    'availability': 'in stock',
                    'brand': product.brand.name,
                    'category': product.category.name,
                    'description': product.description or product.name,
                    'image_url': product.image.url,
                    'name': product.name,
                    'price': int(float(product.price) * 100),
                    'currency': 'KES',
                    'condition': 'new',
                    'inventory': product.in_stock,
                    'url': "https://makinika.com",
                    'retailer_product_group_id': product.sku,
                }
            }
        ]
    }
    response = requests.request(
        "POST",
        url,
        json=payload
    )
    print(response.text)
