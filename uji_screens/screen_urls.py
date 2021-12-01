
def get_screens():
    from .screens import (
        FinishOrderScreen,
        OrderQuantityScreen,
        ConfirmOrderScreen,
        SelectUjiScreen,
    )
    return [
        FinishOrderScreen,
        OrderQuantityScreen,
        ConfirmOrderScreen,
        SelectUjiScreen
    ]
