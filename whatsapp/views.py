import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from buyers.utils import get_buyer, get_buyer_async
from gas_screens.utils import get_last_order_screen, get_last_ordered_from_order
from m_sessions.models import SessionState
from screens.utils import get_screen
from .utils import send_whatsapp
from screens.screens import Screen
from m_sessions.sessions import Session as BaseSession
import json

import asyncio


class Session(BaseSession):
    def render(self, screen):
        """gets the screen type and renders the screen"""
        if not screen:
            return ''
        self.session_state.update(
            state=screen.state,
            data=screen.data
        )
        screen.set_context(self.context)
        return screen.render()


@csrf_exempt
def whatsapp_bot_status(request):
    return HttpResponse(status=200, content="Successful")


def _get_message_body(session_id, phone_number, text, name=None):
    # get the buyer from the phone number
    buyer = get_buyer(phone_number)
    if name and not buyer.name:
        buyer.name = name
        buyer.save()
    # session id is the buyer id
    session = Session(
        session_id,
        context={
            'buyer': buyer,
            'product': get_last_ordered_from_order(buyer)
        }
    )
    # get the session session_state
    session_state: SessionState = session.get_session()
    # check if in trigger word
    trigger_words = ['hi', 'hallo', 'gas']
    # check if time is expired based on time difference
    if text.lower().strip() in trigger_words:
        # if any trigger words are found reset the session_state
        session_state.reset()
    # check if whatsapp response has taken too long
    elif session.session_state.is_expired():
        # reset the session_state
        session_state.reset()

    if not session_state.state:
        # check if the user made a previous order and
        # encourage the user to continue with purchase
        last_product = session.context['product']
        if last_product:
            screen = get_last_order_screen(last_product)
            return session.render(screen)
        # return the default first screen
        screen = get_screen('choose_provider')
        return session.render(screen)
    # get current session
    current_screen: Screen = session.current_screen
    try:
        text = int(text)
    except ValueError:
        return session.render(current_screen)
    # get the next screen
    next_screen = current_screen.next_screen(text)
    if not next_screen:
        return session.render(next_screen)
    return session.render(next_screen)


def bot_processing(request):
    data = json.loads(request.body)
    sender = data["contacts"][0]
    from_phone = sender["wa_id"]
    session_id = f"whatsapp:{sender}"
    name = sender["profile"]["name"]
    text = data["messages"][0]["text"]["body"]
    message = _get_message_body(session_id, from_phone, text, name)
    if message:
        send_whatsapp(
            to=from_phone,
            message=message
        )
    return ''


bot_processing_async = sync_to_async(bot_processing, thread_sensitive=False)


@csrf_exempt
def whatsapp_bot_sync(request):
    data = json.loads(request.body)
    if data.get("statuses"):
        return HttpResponse("Success")
    try:
        sender = data["contacts"][0]
        from_phone = sender["wa_id"]
        text = data["messages"][0]["text"]["body"]
        if text:
            # run function without async
            send_whatsapp(from_phone, f'processing ... {text}')
        bot_processing(request)
    except Exception:
        print("-" * 60)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
    return HttpResponse("Success")


@sync_to_async
@csrf_exempt
@async_to_sync
async def whatsapp_bot_async(request):
    try:
        data = json.loads(request.body)
        if data.get("statuses"):
            return HttpResponse("Success")
        sender = data["contacts"][0]
        text = data["messages"][0]["text"]["body"]
        from_phone = sender["wa_id"]
        if text:
            send_whatsapp(from_phone, f'processing ... {text}')
        loop = asyncio.get_event_loop()
        loop.create_task(bot_processing_async(request))
    except Exception:
        print("-" * 60)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
    return HttpResponse("Successful")

whatsapp_bot = whatsapp_bot_async
