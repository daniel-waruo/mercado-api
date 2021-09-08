import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.utils import get_buyer
from gas_screens.utils import get_last_ordered_from_order
from gas_screens.views import get_message_body as get_gas_message
from egg_screens.views import get_message_body as get_egg_message
from .utils import send_whatsapp, get_hook_data
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
            data=screen.data,
            context=self.session_state.context
        )
        screen.set_context(self.context)
        return screen.render()


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
    # check if in trigger word and set session appropriately
    trigger_words = ['eggs', 'gas', 'hi']
    # check if time is expired based on time difference
    if text.lower().strip() in trigger_words:
        context = text.lower().strip()
        if context == 'hi':
            context = 'gas'
        session_state = session.session_state
        session_state.update(None, None, context=context)

    # check if whatsapp response has taken too long
    if session.session_state.is_expired():
        send_whatsapp(buyer.phone_number, f'Hi {buyer.name},\nYou took too long to response.\n Going back to HOME')
        # reset the session_state
        session.reset()
    if session.session_state.context == 'eggs':
        message = get_egg_message(session, buyer, text)
    else:
        message = get_gas_message(session, buyer, text)
    if message:
        send_whatsapp(to=phone, message=message)


bot_processing_async = sync_to_async(bot_processing, thread_sensitive=False)


@csrf_exempt
def whatsapp_bot_async(request):
    try:
        data = json.loads(request.body)
        if data.get("statuses"):
            return HttpResponse("Success")
        bot_processing(request)
        # loop = asyncio.get_event_loop()
        # loop.create_task(bot_processing_async(request))
    except Exception as e:
        print("-" * 60)
        print(e)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
    return HttpResponse("Successful")


whatsapp_bot = whatsapp_bot_async
