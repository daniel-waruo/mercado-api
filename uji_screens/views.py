from buyers.models import Buyer
from m_sessions.sessions import Session
from screens.screens import Screen
from .utils import get_screen


def get_message_body(session: Session, buyer: Buyer, text: str):
    print("get uji message")
    if not session.state:
        print("new session: return the select uji page")
        screen = get_screen('choose_uji')
        return session.render(screen)
    # get current session
    current_screen: Screen = session.current_screen(get_screen_func=get_screen)
    try:
        # get the next screen
        next_screen = current_screen.next_screen(text)
        if not next_screen:
            session.reset()
    except Exception:
        next_screen = current_screen
        session.reset()
    return session.render(next_screen)
