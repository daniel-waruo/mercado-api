from django.conf import settings
from .screens import Screen


def _get_screen(state: str, screen_urls: list, data: dict, errors=None):
    """searches the screen_urls list and returns the screen"""
    states = [x.state for x in screen_urls]
    if state in states:
        screen_index = states.index(state)
        screen_class = screen_urls[screen_index]
        return screen_class(data, errors)
    raise Exception("invalid screen url name not found in urls")


def get_screen(state, data=None, errors=None, screen_urls=None):
    if screen_urls is None:
        screen_module = __import__(settings.SCREEN_URLS_PATH, globals(), locals(), ['urls'], 0)
        screen_urls = screen_module.screens
    return _get_screen(state=state, screen_urls=screen_urls, data=data, errors=errors)
