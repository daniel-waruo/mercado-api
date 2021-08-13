from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from buyers.utils import get_buyer
from gas_screens.utils import get_last_order_screen, get_last_ordered_from_order
from m_sessions.models import SessionState
from screens.utils import get_screen
from .utils import send_whatsapp
from screens.screens import Screen
from m_sessions.sessions import Session


@csrf_exempt
def whatsapp_bot_status(request):
    return HttpResponse(status=200, content="Successful")


def _get_message_body(request):
    # get phone number and test from the request
    session_id = request.POST.get('From')
    phone_number = session_id.split(':')[1]
    text = request.POST.get('Body')
    # get the buyer from the phone number
    buyer = get_buyer(phone_number)
    # session id is the buyer id
    session = Session(
        session_id,
        context={
            'buyer': buyer,
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

    # get current session
    current_screen: Screen = session.current_screen
    try:
        text = int(text)
    except ValueError:
        return session.render(current_screen)
    # get the next screen
    next_screen = current_screen.next_screen(text)
    return session.render(next_screen)


@csrf_exempt
def whatsapp_bot(request):
    message = _get_message_body(request)
    send_whatsapp(
        from_=request.POST.get('To'),
        to_=request.POST.get('From'),
        message=message
    )
    return HttpResponse("Successful")
