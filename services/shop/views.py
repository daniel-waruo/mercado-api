from buyers.models import Buyer
from m_sessions.sessions import Session
from services.shop.screens import Screen
from services.utils import get_screen


def get_message_body(session: Session, buyer: Buyer, message: dict):
    if message.get('type') == 'order':
        screen = get_screen(
            'get_location',
            data={
                'order': message['order']
            })
        session.reset()
        return session.render(screen)
    # get current session
    current_screen: Screen = session.current_screen(get_screen_func=get_screen)
    # get the next screen
    next_screen: Screen = current_screen.next_screen(message)
    if not next_screen:
        session.reset()

    return session.render(next_screen)
