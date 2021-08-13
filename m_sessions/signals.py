import django.dispatch

request_finished = django.dispatch.Signal(
    providing_args=['session']
)
