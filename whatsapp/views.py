import sys
import threading
import traceback

from asgiref.sync import sync_to_async
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
        data = get_hook_data(request)
        if not data:
            return
        phone, session_id, name, input_message = data
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

        if not message:
            if session.session_state.state:
                message = get_message_body(session, buyer, input_message)
            else:
                session.reset()
                screen = get_screen('shop_menu')
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


@csrf_exempt
def whatsapp_bot(request):
    if request.method == "GET":
        return HttpResponse(request.GET.get('hub.challenge'))
    t = threading.Thread(target=bot_processing, args=[request], daemon=True)
    t.start()
    return HttpResponse(status=200)
