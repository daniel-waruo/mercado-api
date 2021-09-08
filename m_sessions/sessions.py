from .http import Response
from .models import SessionState
from screens.utils import get_screen


class Session:
    def __init__(self, session_id: str, context: dict = None):
        self._session_id: str = session_id
        self.context = context
        self._session_state = self.session_state

    @property
    def state(self):
        return self.session_state.state

    @property
    def session_state(self):
        if hasattr(self, '_session_state'):
            return self._session_state
        session, created = SessionState.objects.get_or_create(
            session_id=self._session_id,
            defaults={
                'state': None,
                'data': None
            }
        )
        return session

    @property
    def current_screen(self):
        return get_screen(self.session_state.state, data=self.session_state.data)

    def render(self, screen):
        """gets the screen type and renders the screen"""
        self.session_state.update(
            state=screen.state,
            data=screen.data
        )
        screen.set_context(self.context)
        response = screen.render()
        return Response(self, response)

    def reset(self):
        self.session_state.reset()
