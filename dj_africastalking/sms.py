from . import africastalking

sms = africastalking.SMS


# Use the service synchronously
def send_sms(to, message, raise_exception=False):
    # Or use it asynchronously
    success = False

    def on_finish(error, response):
        if raise_exception and error is not None:
            raise error
        if not error:
            global success
            success = True

    sms.send(message, [to], callback=on_finish)

    return success
