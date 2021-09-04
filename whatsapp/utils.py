import requests
import json
from django.conf import settings


def send_whatsapp(to: str, message: str):
    url = "https://waba.360dialog.io/v1/messages"
    payload = json.dumps({
        "to": to,
        "type": "text",
        "recipient_type": "individual",
        "text": {
            "body": message
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'D360-API-KEY': settings.WABA_API_KEY
    }
    try:
        requests.request("POST", url, headers=headers, data=payload, timeout=1000)
    except ConnectionError:
        print("failed connection")
