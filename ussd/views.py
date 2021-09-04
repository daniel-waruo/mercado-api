from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from buyers.utils import get_buyer
from m_sessions.http import Response

from screens.screens import Screen
from gas_screens.utils import get_screen, get_last_order_screen, get_last_ordered_from_order
from m_sessions.sessions import Session as BaseSession
from gas_screens.screens import Screen


class Session(BaseSession):
    def render(self, screen: Screen):
        """gets the screen type and renders the screen"""
        self.session_state.update(
            state=screen.state,
            data=screen.data
        )
        screen.set_context(self.context)
        response = screen.render_ussd()
        return Response(self, response)


@csrf_exempt
def ussd_bot(request):
    code = "gas"
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber')
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
            last_product = get_last_ordered_from_order(buyer)
            if last_product:
                screen = get_last_order_screen(last_product)
                session.context = {
                    **session.context,
                    'product': last_product
                }
                return session.render(screen)
            # return the default first screen
            screen = get_screen('choose_provider')
            return session.render(screen)
        else:
            # get current_text
            current_input = text.split("*")[-1]
            # get current session
            current_screen: Screen = session.current_screen
            try:
                current_input = int(current_input)
            except ValueError:
                return session.render(current_screen)
            # get the next screen
            next_screen = current_screen.next_screen(current_input)
            return session.render(next_screen)
    return HttpResponse("Invalid HTTP method", status=403)
