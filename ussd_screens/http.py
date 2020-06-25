from django.http import HttpResponse
from .signals import request_finished


# use custom response class to override HttpResponse.close()
class Response(HttpResponse):
    def __init__(self, session, content, **kwargs):
        super(Response, self).__init__(content=content, **kwargs)
        self.ussd_session = session

    def close(self):
        super(Response, self).close()
        # do whatever you want, this is the last codepoint in request handling
        request_finished.send(
            sender=self.__class__,
            session=self.ussd_session
        )
