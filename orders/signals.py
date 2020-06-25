import django.dispatch

checkout_request = django.dispatch.Signal(providing_args=["buyer", 'order'])
