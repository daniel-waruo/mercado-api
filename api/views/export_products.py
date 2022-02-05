import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse

from products.models import Product
from products.utils import update_facebook_catalog, update_facebook_batch


def export_products(request: WSGIRequest):
    if request.method == 'POST':
        products = Product.objects.all()
        data = json.loads(request.body)
        update_facebook_batch(
            products,
            "886770702008655",
            data.get('accessToken')
        )
        return JsonResponse({
            'message': 'Successfully Uploaded Products'
        })
    return JsonResponse({
        'message': 'USE POST'
    })
