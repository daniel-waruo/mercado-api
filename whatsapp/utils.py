from twilio.rest import Client

import os

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']


def send_whatsapp(from_: str, to_: str, message: str):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=from_,
        to=to_
    )
