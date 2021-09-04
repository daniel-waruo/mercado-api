import datetime
from base64 import b64encode

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


class MpesaConfig(object):

    def __init__(self, short_code, consumer_key, consumer_secret, pass_key):
        self.short_code = short_code
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.pass_key = pass_key


class STK(object):
    def __init__(self, config: MpesaConfig, base_url):
        self.config = config
        self.base_url = base_url

    @property
    def access_token(self):
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(
            url,
            auth=HTTPBasicAuth(
                self.config.consumer_key,
                self.config.consumer_secret
            )
        )
        print(response.headers)
        return response.json()["access_token"]

    def _encoded_password(self, time_now):
        s = self.config.short_code + self.config.pass_key + time_now
        return b64encode(s.encode('utf-8')).decode('utf-8')

    def get_time_now(self):
        return datetime.datetime.now().strftime("%Y%m%d%H%I%S")

    def initiate(self, phone_number, amount, callback_url, account_ref, description=None):
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        time_now = self.get_time_now()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        request = {
            "BusinessShortCode": self.config.short_code,
            "Password": self._encoded_password(time_now),
            "Timestamp": time_now,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(int(amount)),
            "PartyA": phone_number,
            "PhoneNumber": phone_number,
            "PartyB": self.config.short_code,
            "CallBackURL": callback_url,
            "AccountReference": account_ref[:24],
            "TransactionDesc": description or f"Payment for {phone_number}"
        }
        response = requests.post(url, json=request, headers=headers)
        return response.json()

    def check_status(self, checkout_request_id):
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        time_now = self.get_time_now()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        request = {
            "BusinessShortCode": self.config.short_code,
            "Password": self._encoded_password(time_now),
            "Timestamp": time_now,
            "CheckoutRequestID": checkout_request_id
        }
        response = requests.post(url, json=request, headers=headers)
        return response.json()


config = MpesaConfig(**settings.DARAJA_CONFIG)
base_url = settings.DARAJA_BASE_URL
stk = STK(config, base_url)


def initiate_stk(phone_number, amount, callback_url, account_ref):
    return stk.initiate(phone_number, amount, callback_url, account_ref)


def check_stk_status(checkout_transaction_id):
    return stk.check_status(checkout_transaction_id)
