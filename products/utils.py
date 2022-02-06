import json

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


def update_facebook_batch(products, catalog_id, access_token, operation='UPDATE'):
    url = f"https://graph.facebook.com/v12.0/{catalog_id}/batch"
    facebook_requests = []

    for product in products:
        facebook_requests.append(
            {
                'method': operation,
                'retailer_id': product.sku,
                'data': {
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
        )
    segments = [facebook_requests[x:x + 6] for x in range(0, len(facebook_requests), 6)]
    for segment in segments:
        facebook_requests = facebook_requests[0:6]
        payload = {
            'access_token': access_token,
            'requests': segment
        }
        response = requests.request(
            "POST",
            url,
            json=payload
        )
        print(json.dumps(payload, indent=3))
        print(response.text)
