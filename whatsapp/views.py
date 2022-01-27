import asyncio
import json
import sys
import traceback

from asgiref.sync import sync_to_async, async_to_sync
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.utils import get_buyer
from egg_screens.views import get_message_body as get_egg_message
from gas_screens.utils import get_last_ordered_from_order
from gas_screens.views import get_message_body as get_gas_message
from m_sessions.sessions import Session as BaseSession
from uji_screens.views import get_message_body as get_uji_message
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
        phone, session_id, name, text, is_interactive = get_hook_data(request)
        # get the buyer from the phone number
        buyer = get_buyer(phone)
        if name and not buyer.name:
            buyer.name = name
            buyer.save()
        # session id is the buyer id
        session = Session(session_id, context={'buyer': buyer})
        # check if in trigger word and set session appropriately
        trigger_words = ['hi', 'hallo', 'makinika', 'hey']
        # restart session in text
        if text.lower().strip() in trigger_words:
            session.session_state.update(None, None, None)
            send_whatsapp(to=phone, body={
                "recipient_type": "individual",
                "to": phone,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {
                        "type": "text",
                        "text": "Patterns Store"
                    },
                    "body": {
                        "text": 'Welcome to Patterns Store'
                    },
                    "action": {
                        "button": "Select Product",
                        "sections": [
                            {
                                "title": "Select Product",
                                "rows": [
                                    {
                                        'id': 'menu:eggs',
                                        'title': 'Eggs (tray)',
                                        'description': 'Get the freshest eggs in town.'
                                    },
                                    {
                                        'id': 'menu:gas',
                                        'title': 'Gas',
                                        'description': 'Get the best gas deals.'
                                    },
                                    {
                                        'id': 'menu:uji',
                                        'title': 'Porridge',
                                        'description': 'Healthy and nutritious.'
                                    }
                                ]
                            },
                        ]
                    }
                }
            })
            return
        context = session.session_state.context
        context = context if context in ['eggs', 'gas', 'uji'] else None
        print(f"new product {context}")
        if is_interactive and text.startswith('menu:'):
            context = text.split(':')[1].lower().strip()
            session_state = session.session_state
            session_state.update(None, None, context=context)
            session.reset()

        session.context['product'] = get_last_ordered_from_order(
            buyer,
            {'items__product__sku__startswith': session.session_state.context}
        )
        print(f"after check {context}")
        if context == 'eggs':
            message = get_egg_message(session, buyer, text)
        elif context == 'gas':
            message = get_gas_message(session, buyer, text)
        else:
            message = get_uji_message(session, buyer, text)
        if message:
            if isinstance(message, dict):
                send_whatsapp(to=phone, body=message)
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
        print(json.dumps(data, indent=2))
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
