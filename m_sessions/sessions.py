from .http import Response
from .models import SessionState
from screens.utils import get_screen


class Session:
    def __init__(self, session_id: str, context: dict = None):
        self._session_id: str = session_id
        self.context = context
        self.session_state = self.get_session()

    @property
    def current_screen(self):
        return get_screen(self.session_state.state, data=self.session_state.data)

    def get_session(self, state=None, data=None):
        session, created = SessionState.objects.get_or_create(
            session_id=self._session_id,
            defaults={
                'state': state,
                'data': data
            }
        )
        return session

    def render(self, screen):
        """gets the screen type and renders the screen"""
        self.session_state.update(
            state=screen.state,
            data=screen.data
        )
        screen.set_context(self.context)
        response = screen.render()
        return Response(self, response)

