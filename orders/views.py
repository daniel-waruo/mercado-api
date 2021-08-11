from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Order
import json


# Create your views here


@csrf_exempt
def confirm_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # get order_id from metadata
        transaction_id = data.get("transactionId")
        category = data.get("category")
        assert category == 'MobileCheckout'
        meta_data = data.get("requestMetadata") or None
        order_id = meta_data.get("order_id")
        assert order_id
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse("ORDER DELETED")
        status = data.get("status")
        # check if status is successful
        if status == "Success":
            mpesa_id = data.get("providerRefId")
            assert mpesa_id
            order.payment_success(
                transaction_id=transaction_id,
                mpesa_id=mpesa_id
            )
        else:
            order.payment_fail(transaction_id)
        return HttpResponse("operation success", status=200)
    else:
        return HttpResponse("Invalid HTTP Method", status=403)
