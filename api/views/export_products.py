import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from products.models import Product
from products.utils import update_facebook_catalog


def export_products(request: WSGIRequest):
    if request.method == 'POST':
        products = Product.objects.all()
        data = json.loads(request.body)
        for product in products:
            try:
                try:
                    update_facebook_catalog(
                        product,
                        "886770702008655",
                        data.get('accessToken'),
                        operation='DELETE'
                    )
                except:
                    pass
                update_facebook_catalog(
                    product,
                    "886770702008655",
                    data.get('accessToken')
                )
            except (ValueError, AttributeError):
                pass
        return JsonResponse({
            'message': 'Successfully Uploaded Products'
        })
    return JsonResponse({
        'message': 'USE POST'
    })
