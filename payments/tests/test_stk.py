from unittest import TestCase

from payments.stk import initiate_stk , check_stk_status


class STKTestCase(TestCase):
    def setUp(self) -> None:
        self.phone_number = '254797792447'
        self.redirect_url = 'https://productgiving.org/'
        self.amount = 10

    def test_initiate_payments(self):
        response = initiate_stk(
            phone_number=self.phone_number,
            amount=self.amount,
            callback_url=self.redirect_url,
            account_ref="Name With Space"
        )
        print(check_stk_status(response['CheckoutRequestID']))
