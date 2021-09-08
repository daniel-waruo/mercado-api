
def get_screens():
    from .screens import (
        FinishOrderScreen,
        OrderQuantityScreen,
        ConfirmOrderScreen,

    )
    return [
        FinishOrderScreen,
        OrderQuantityScreen,
        ConfirmOrderScreen,
    ]
