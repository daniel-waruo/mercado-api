import json

import requests
from django.conf import settings


def send_whatsapp(to: str, message: str = None, body=None):
    url = "https://waba.360dialog.io/v1/messages"
    if message:
        payload = json.dumps({
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
        payload = json.dumps(body,indent=2)
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
    is_interactive = False
    if data.get("contacts"):
        sender = data["contacts"][0]
        phone = sender["wa_id"]
        session_id = f"whatsapp:{phone}"
        name = sender["profile"]["name"]
        message = data["messages"][0]
        if message.get('interactive'):
            if message["interactive"]["type"] == "list_reply":
                text = message["interactive"]["list_reply"]["id"]
            else:
                text = message["interactive"]["button_reply"]["id"]
            is_interactive = True
        else:
            text = message["text"]["body"]
        return phone, session_id, name, text, is_interactive
    return None
