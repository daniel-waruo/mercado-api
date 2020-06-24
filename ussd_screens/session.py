from django.http import HttpResponse

from .models import USSDState
from .utils import get_screen


class USSDSession:
    def __init__(self, session_id: str):
        self._session_id: str = session_id

    @property
    def session(self):
        return self.get_session()

    @property
    def current_screen(self):
        session = self.session
        return get_screen(session.state, data=session.data)

    def get_session(self, state=None, data=None):
        session, created = USSDState.objects.get_or_create(
            session_id=self._session_id,
            defaults={
                'state': state,
                'data': data
            }
        )
        return session

    def render(self, screen):
        if screen.type == "CON":
            return self.con(screen)
        elif screen.type == "END":
            return self.end(screen)
        raise Exception("invalid screen type")

    def con(self, screen):
        self.session.update(
            state=screen.state,
            data=screen.data
        )
        response = "CON " + screen.render()
        return HttpResponse(response)

    def end(self, screen):
        self.end_session()
        response = "END " + screen.render()
        return HttpResponse(response)

    def end_session(self):
        self.session.delete()
