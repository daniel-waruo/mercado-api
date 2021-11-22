from buyers.models import Buyer
from m_sessions.sessions import Session
from screens.screens import Screen
from .utils import get_screen


def get_message_body(session: Session, buyer: Buyer, text: str):
    if not session.state:
        # return the default first screen
        screen = get_screen('order_quantity')
        return session.render(screen)
    # get current session
    current_screen: Screen = session.current_screen(get_screen_func=get_screen)
    # make sure input is an integer
    try:
        text = int(text)
    except ValueError:
        return session.render(current_screen)
    # get the next screen
    next_screen = current_screen.next_screen(text)
    if not next_screen:
        session.reset()
    return session.render(next_screen)
