from typing import Dict

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from buyers.utils import get_buyer
from django.template.loader import render_to_string

from ussd_screens.screens import Screen
from ussd_screens.utils import get_screen
from ussd_screens.session import USSDSession

GAS_CYLINDERS = ['Total', 'Pro-Gas', 'K-Gas']

GAS_SIZES_PRICES: Dict[str, str] = {
    '6': '1,000',
    '13': '2170',
    '22.5': '3,760',
    '50': '8350'
}


# Create your views here.
@csrf_exempt
def index(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        service_code = request.POST.get('serviceCode')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text')

        # register the buyer into our system
        buyer = get_buyer(phone_number)

        args = text.split("*")

        session = USSDSession(session_id)

        if text == "":
            # empty string means user has not chosen
            # show the default start screen
            screen = get_screen('choose_provider')
            return session.con(screen)
        else:
            # get current_text
            current_input = text.split("*")[-1]
            # get current session
            current_screen: Screen = session.current_screen
            try:
                current_input = int(current_input)
            except ValueError:
                session.render(current_screen)
            # get the next screen
            next_screen = current_screen.next_screen(current_input)
            return session.render(next_screen)
    return HttpResponse("Use POST Request")
