from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from buyers.utils import get_buyer
from gas_screens.screens import Screen
from gas_screens.utils import get_screen, get_last_order_screen, get_last_ordered_from_order
from egg_screens.utils import get_screen as get_screen_eggs
from m_sessions.http import Response
from m_sessions.sessions import Session as BaseSession
from screens.screens import Screen


class Session(BaseSession):
    def render(self, screen: Screen):
        """gets the screen type and renders the screen"""
        self.session_state.update(
            state=screen.state,
            data=screen.data,
            context=self.context
        )
        screen.set_context(self.context)
        response = screen.render_ussd()
        return Response(self, response)


@csrf_exempt
def ussd_bot_gas(request):
    code = "gas"
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber')[1:]
        session_id = f"{code}:{phone_number}"
        text = request.POST.get('text')
        # get buyer from the system
        buyer = get_buyer(phone_number)
        # initialize the gas session
        session = Session(
            session_id,
            context={
                'buyer': buyer,
            }
        )
        # load the default screen
        if text == "":
            # if new gas session clear the session state
            session.session_state.reset()
            # this is the first screen to be shown
            last_product = get_last_ordered_from_order(
                buyer,
                dict(
                    items__product__sku__startswith='gas'
                ),
            )
            if last_product:
                screen = get_last_order_screen(last_product)
                session.context = {
                    **session.context,
                    'product': last_product
                }
                return session.render(screen)
            # return the default first screen
            screen = get_screen('choose_cylinder')
            return session.render(screen)
        else:
            # get current_text
            current_input = text.split("*")[-1]
            # get current session
            current_screen: Screen = session.current_screen()
            try:
                current_input = int(current_input)
            except ValueError:
                return session.render(current_screen)
            # get the next screen
            next_screen = current_screen.next_screen(current_input)
            return session.render(next_screen)
    return HttpResponse("Invalid HTTP method", status=403)


@csrf_exempt
def ussd_bot_eggs(request):
    code = "eggs"
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber')[1:]
        session_id = f"{code}:{phone_number}"
        text = request.POST.get('text')
        # get buyer from the system
        buyer = get_buyer(phone_number)
        # initialize the gas session
        session = Session(
            session_id,
            context={
                'buyer': buyer,
            }
        )
        # load the default screen
        if not text:
            # if new gas session clear the session state
            session.session_state.reset()
            # return the default first screen
            screen = get_screen_eggs('order_quantity')
            return session.render(screen)
        else:
            # get current_text
            current_input = text.split("*")[-1]
            # get current session
            current_screen: Screen = session.current_screen(
                get_screen_func=get_screen_eggs
            )
            try:
                current_input = int(current_input)
            except ValueError:
                return session.render(current_screen)
            # get the next screen
            next_screen = current_screen.next_screen(current_input)
            return session.render(next_screen)
    return HttpResponse("Invalid HTTP method", status=403)
