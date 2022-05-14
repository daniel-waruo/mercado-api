import django.dispatch

checkout_request = django.dispatch.Signal(providing_args=['order'])

payment_fail = django.dispatch.Signal(providing_args=['order'])

payment_success = django.dispatch.Signal(providing_args=['order'])

payment_pending = django.dispatch.Signal(providing_args=['order'])

order_shipping = django.dispatch.Signal(providing_args=['order'])

order_cancel = django.dispatch.Signal(providing_args=['order'])

order_delivered = django.dispatch.Signal(providing_args=['order'])

order_requested = django.dispatch.Signal(providing_args=['order'])
