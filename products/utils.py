from urllib.parse import urlencode

import requests

from products.models import Product

catalog_id = ""


def update_facebook_catalog(product: Product, cat):
    access_token = "EAAIVJzFWSBEBACQZC9mZCinyc7HYvPfxQ2BZCmi6ZCgNm2PcP4IUPZCqN0Mj9heQSQOcJQkUkfjbp1ehaSy0AqRsZAcYZAdm1Jo7oiYmsPbGCvN0r3p85TxgpocbIdv0L6WEN7YB1bOWaDBKD0aTTkqvVOuAykGqjeWm9AV69F3ohp0vB68V1yhsAz38gGAkdRwMrId7TSkAFFRlzWJ9MJ5"
    url_string = urlencode(
        {'access_token': access_token}
    )
    url = f"https://graph.facebook.com/v12.0/{catalog_id}/batch"
    payload = {
        'access_token': access_token,
        'requests': [
            {
                'method': 'CREATE',
                'retailer_id': product.sku,
                'data': {
                    'availability': 'in stock',
                    'brand': product.brand.name,
                    'category': product.category.name,
                    'description': product.description,
                    'image_url': product.image.url,
                    'name': product.name,
                    'price': product.price,
                    'currency': 'KES',
                    'condition': 'new',
                    'url': "product view url",
                    'retailer_product_group_id': product.sku,
                }
            }
        ]
    }
    headers = {}

    response = requests.request(
        "POST",
        url,
        headers=headers,
        json=payload
    )
    print(response.text)
