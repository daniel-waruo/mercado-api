import asyncio
import json
import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.utils import get_buyer
from m_sessions.sessions import Session as BaseSession
from shop.views import get_message_body
from .parsers import parse
from .utils import send_whatsapp, get_hook_data


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
    try:
        phone, session_id, name, message = get_hook_data(request)
        # get the buyer from the phone number
        buyer = get_buyer(phone)
        if name and not buyer.name:
            buyer.name = name
            buyer.save()
        # set buyer in the session
        session = Session(session_id, context={'buyer': buyer})
        # check if in trigger word and set session appropriately
        trigger_words = ['hi', 'hallo', 'makinika', 'hey']
        # check if message was parsed as a text if so evaluate as one
        text = parse(message, "text")
        if text and isinstance(text, str):
            if text.lower().strip() in trigger_words:
                session.reset()
        message = get_message_body(session, buyer, message)
        if message:
            if isinstance(message, dict):
                send_whatsapp(to=phone, body=message)
                return
            if isinstance(message, list):
                for mess in message:
                    send_whatsapp(to=phone, body=mess)
                return
            send_whatsapp(to=phone, message=message)
    except Exception as e:
        print("-" * 60)
        print(e)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)


bot_processing_async = sync_to_async(bot_processing, thread_sensitive=False)


async def whatsapp_bot_async(request):
    try:
        data = json.loads(request.body)
        if data.get("statuses"):
            return HttpResponse("Success")
        # bot_processing(request)
        loop = asyncio.get_event_loop()
        loop.create_task(bot_processing_async(request))
    except Exception as e:
        print("-" * 60)
        print(e)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)
    return HttpResponse("Successful")


whatsapp_bot = csrf_exempt(async_to_sync(whatsapp_bot_async))
