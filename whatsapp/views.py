import asyncio
import json
import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.utils import get_buyer
from m_sessions.sessions import Session as BaseSession
from services.shop.views import get_message_body
from services.utils import get_screen
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
        phone, session_id, name, input_message = get_hook_data(request)
        # get the buyer from the phone number
        buyer = get_buyer(phone)
        if name and not buyer.name:
            buyer.name = name
            buyer.save()
        # set buyer in the session
        session = Session(
            session_id,
            context={'buyer': buyer}
        )
        # check if in trigger word and set session appropriately
        trigger_words = ['hi', 'hallo', 'makinika', 'hey']
        # check if message was parsed as a text if so evaluate as one
        text = parse(input_message, "text")
        if text and isinstance(text, str):
            if text.lower().strip() in trigger_words:
                session.reset()
        message = None
        if parse(input_message, "interactive"):
            text = parse(input_message, "interactive")
            if "menu:" in text:
                session.reset()
                screen = text.split(':')[0]
                current_screen = get_screen(screen)
                next_screen = current_screen.next_screen(text)
                message = session.render(next_screen)

        if not message:
            if session.session_state.state:
                print("WHY BOT")
                message = get_message_body(session, buyer, input_message)
            else:
                print("ELSE WHY")
                screen = get_screen('main_menu')
                message = session.render(screen)
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
