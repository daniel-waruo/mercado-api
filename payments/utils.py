import json
import uuid

from django.conf import settings

from orders.models import Order
from payments.models import (
    OrderTransaction,
    Transaction
)
from payments.stk import initiate_stk, check_stk_status


def pay_via_transaction(transaction: Transaction, callback_url, account_ref):
    try:
        # get phone number and remove the + sign if it
        # comes with it
        phone_number = transaction.phone
        if phone_number.startswith("+"):
            phone_number = phone_number[1:]
        if phone_number.startswith("0"):
            phone_number = f"254{phone_number[1:]}"
        # send the stk push request to safaricom
        response = initiate_stk(
            phone_number=phone_number,
            amount=transaction.amount,
            account_ref=account_ref,
            callback_url=callback_url
        )
        print("Payment Response")
        print(json.dumps(response, indent=3))
        # if response is successful set transaction pending
        if response.get('ResponseCode') == '0':
            transaction.set_pending(
                merchant_request_id=response['MerchantRequestID'],
                checkout_request_id=response['CheckoutRequestID']
            )
            return True, transaction
        # set transaction as failed and set the error message
        transaction.set_fail(
            merchant_request_id=None,
            checkout_request_id=None,
            reason_failed=response.get('errorMessage')
        )
        return False, transaction
    except Exception as e:
        message = str(e.args)
        transaction.set_fail(
            merchant_request_id=None,
            checkout_request_id=None,
            reason_failed=message
        )
        return False, transaction


def pay_for_order(order: Order, phone: str):
    """ Initiates a payment for a particular Order
    Args:
        order - the order we are going to pay for
    Returns:
        tuple(success_status,transaction) - returns a success message and the transaction
    """
    # create an order transaction from an order
    transaction = OrderTransaction.objects.create(
        amount=order.get_order_total(),
        order=order,
        phone=phone
    )
    # get callback url stk push is going to use
    callback_url = f'{settings.CALLBACK_BASE_URL}/callback/order'
    # pay for the order
    return pay_via_transaction(transaction, callback_url, account_ref="MAKINIKA TECH")


def update_transaction_status(transaction: Transaction):
    response = check_stk_status(
        checkout_transaction_id=transaction.checkout_request_id
    )
    response = dict(**response)
    response_code = response.get("ResultCode")
    if response_code is None:
        return transaction
    elif response_code != '0':
        merchant_request_id = response["MerchantRequestID"]
        checkout_request_id = response["CheckoutRequestID"]
        transaction.set_fail(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id,
            reason_failed=response['ResponseDescription']
        )
        return transaction
    elif response_code == '0':
        merchant_request_id = response["MerchantRequestID"]
        checkout_request_id = response["CheckoutRequestID"]
        transaction.set_success(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id,
            mpesa_code=uuid.uuid4()
        )
        return transaction
    return transaction
