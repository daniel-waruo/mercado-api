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


def get_hook_data(request):
    data = json.loads(request.body)
    sender = data["contacts"][0]
    phone = sender["wa_id"]
    session_id = f"whatsapp:{sender}"
    name = sender["profile"]["name"]
    text = data["messages"][0]["text"]["body"]
    return phone, session_id, name, text
