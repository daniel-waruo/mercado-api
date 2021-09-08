from buyers.models import Buyer
from gas_screens.utils import get_last_order_screen, get_last_ordered_from_order
from m_sessions.sessions import Session
from screens.utils import get_screen
from screens.screens import Screen


def get_message_body(session: Session, buyer: Buyer, text: str):
    if not session.state:
        # check if the user made a previous order and
        # encourage the user to continue with purchase
        last_product = session.context['product']
        if last_product:
            screen = get_screen(
                'last_order',
                data={'product_id': last_product.id}
            )
            return session.render(screen)
        # return the default first screen
        screen = get_screen('choose_cylinder')
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
        return session.render(next_screen)
    return session.render(next_screen)
