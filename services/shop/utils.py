import json

import requests
from woocommerce import API

wcapi = API(
    url="https://wakini.makinika.com",
    consumer_key="ck_66f6d0b81ef643dfe188bc0d5df90fa44071bb29",
    consumer_secret="cs_64d220b2e07808a202bacd7afbd240359c17f60f",
    version="wc/v3"
)

access_token = 'EAAIEfrPBqW4BAKqq4F6V2ZBiTakE0Yo5REzzzs2kdcfibZAmVmIZCRQ9HOu4GP0KwHDqKNju9Cw94NAGHktbgS1mknZB0eJ3dpk7ZAbTbZCTe0ZA4TgZCabtLTZB3CXsHKizOMWxuAD8LtTdaF7gZCGtRbEOZBNqI4uMkGagr8LllZAjcWNZBJXl2Tj6J'


def fetch_categories(**kwargs):
    return wcapi.get("products/categories", params=kwargs).json()


def get_category(category_id):
    print(category_id)
    return wcapi.get(f"products/categories/{category_id}").json()


def fetch_products(**kwargs):
    return wcapi.get("products", params=kwargs).json()


def update_facebook_batch_from_woo(catalog_id="400741145334561", operation='CREATE'):
    products = wcapi.get("products").json()
    print("fetched products")
    print(json.dumps(products, indent=3))
    url = f"https://graph.facebook.com/v14.0/{catalog_id}/batch"
    facebook_requests = list(
        map(
            lambda product: {
                'method': operation,
                'retailer_id': str(product["slug"]),
                'data': {
                    'availability': 'in stock',
                    'category': product["categories"][-1]["name"],
                    'description': product["short_description"],
                    'image_url': product["images"][0]["src"],
                    'additional_image_urls': list(map(lambda image: image["src"], product["images"])),
                    'name': product["name"],
                    'price': int(product["price"]),
                    'sale_price': int(product["price"]),
                    'currency': 'KES',
                    'condition': 'new',
                    'inventory': product["stock_quantity"],
                    'url': product["permalink"],
                    'retailer_product_group_id': str(product["slug"]),
                }
            }, products
        )
    )
    payload = {
        'access_token': access_token,
        'requests': facebook_requests
    }

    response = requests.request(
        "POST",
        url,
        json=payload
    )
    print(json.dumps(payload, indent=3))
    print(response.text)
