from .models import SessionState


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
        session, created = SessionState.objects.get_or_create(
            session_id=self._session_id,
            defaults={
                'state': None,
                'data': None,
                'buyer': self.context.get('buyer')
            }
        )
        return session

    def current_screen(self, get_screen_func=None):
        from screens.utils import get_screen
        if get_screen_func:
            get_screen = get_screen_func
        return get_screen(
            self.session_state.state,
            data=self.session_state.data,
            context=self.context
        )

    def render(self, screen):
        """gets the screen type and renders the screen"""
        if not screen:
            return None
        self.session_state.update(
            state=screen.state,
            data=screen.data,

        )
        screen.set_context(self.context)
        return screen.render()

    def reset(self):
        self.session_state.reset()

    def update(self, state, data, context):
        self.session_state.update(state, data, context)
