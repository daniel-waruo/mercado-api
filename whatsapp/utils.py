import json

import requests

from buyers.models import Message

WABA_PHONE_ID = '110400311680161'
FACEBOOK_ACCESS_TOKEN = 'EAAIEfrPBqW4BAKqq4F6V2ZBiTakE0Yo5REzzzs2kdcfibZAmVmIZCRQ9HOu4GP0KwHDqKNju9Cw94NAGHktbgS1mknZB0eJ3dpk7ZAbTbZCTe0ZA4TgZCabtLTZB3CXsHKizOMWxuAD8LtTdaF7gZCGtRbEOZBNqI4uMkGagr8LllZAjcWNZBJXl2Tj6J'


def send_whatsapp(to: str, message: str = None, body=None):
    url = f"https://graph.facebook.com/v13.0/{WABA_PHONE_ID}/messages"
    if message:
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "recipient_type": "individual",
            "text": {
                "body": message
            }
        })
    else:
        if not body.get('to'):
            body['to'] = to
        body["messaging_product"] = "whatsapp"
        payload = json.dumps(body, indent=2)
        print(payload)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {FACEBOOK_ACCESS_TOKEN}"
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=1000)
        print(response.text)
    except ConnectionError:
        print("failed connection")


def get_hook_data(request):
    data = json.loads(request.body)
    data = data["entry"][0]["changes"][0]["value"]
    if data.get("contacts"):
        sender = data["contacts"][0]
        phone = sender["wa_id"]
        session_id = f"whatsapp:{phone}"
        name = sender["profile"]["name"]
        message = data["messages"][0]
        if not Message.objects.filter(message_id=message["id"]).exists():
            Message.objects.create(message_id=message["id"])
            return phone, session_id, name, message
    return None
