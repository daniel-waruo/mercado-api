import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.models import Buyer
from buyers.utils import get_buyer
from gas_screens.utils import get_last_order_screen, get_last_ordered_from_order
from screens.utils import get_screen
from .utils import send_whatsapp, get_hook_data
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


def _get_message_body(session: Session, buyer: Buyer, text: str):
    # check if whatsapp response has taken too long
    if session.session_state.is_expired():
        send_whatsapp(buyer.phone_number, f'Hi {buyer.name},\nYou took too long to response.\n Going back to HOME')
        # reset the session_state
        session.reset()

    if not session.state:
        # check if the user made a previous order and
        # encourage the user to continue with purchase
        last_product = session.context['product']
        if last_product:
            screen = get_last_order_screen(last_product)
            return session.render(screen)
        # return the default first screen
        screen = get_screen('choose_cylinder')
        return session.render(screen)
    # get current session
    current_screen: Screen = session.current_screen
    # make sure input is an integer
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
    phone, session_id, name, text = get_hook_data(request)
    # get the buyer from the phone number
    buyer = get_buyer(phone)
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
    # check if in trigger word
    trigger_words = ['hi', 'hallo', 'gas']
    # check if time is expired based on time difference
    if text.lower().strip() in trigger_words:
        # if any trigger words are found reset the session_state
        session.reset()
    message = _get_message_body(session, buyer, text)
    if message:
        send_whatsapp(to=phone, message=message)


bot_processing_async = sync_to_async(bot_processing, thread_sensitive=False)


@sync_to_async
@csrf_exempt
@async_to_sync
async def whatsapp_bot_async(request):
    try:
        data = json.loads(request.body)
        if data.get("statuses"):
            return HttpResponse("Success")
        loop = asyncio.get_event_loop()
        loop.create_task(bot_processing_async(request))
    except Exception as e:
        print("-" * 60)
        print(e)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
    return HttpResponse("Successful")


whatsapp_bot = whatsapp_bot_async
