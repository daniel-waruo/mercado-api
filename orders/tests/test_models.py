from django.test import TestCase

from buyers.models import Buyer
from items.models import Item, ComplementaryItem
from orders.models import Order, OrderItem, OrderMpesaTransaction


class OrderTestCase(TestCase):
    def setUp(self) -> None:
        self.buyer = Buyer.objects.create(
            phone_number="+254797792447"
        )
        self.order = Order.objects.create(
            buyer=self.buyer
        )
        self.item = Item.objects.create(
            name='Test Product',
            price=200
        )

    def test_make_order(self):
        order = Order.objects.make_order(
            buyer=self.buyer,
            item=self.item
        )
        self.assertIsInstance(order, Order)
        self.assertIsNotNone(order)

    def test_add_item(self):
        order_item = self.order.add_item(
            item=self.item
        )
        self.assertIsInstance(order_item, OrderItem)
        self.assertEqual(order_item.order.id, self.order.id)

    def test_get_order_total(self):
        self.order.add_item(item=self.item)
        c_item = ComplementaryItem.objects.create(
            item=self.item,
            name='Test Comp Item',
            price=200
        )
        self.order.add_item(item=c_item)
        self.assertIsNotNone(self.order.get_order_total())
        self.assertEqual(self.item.price + c_item.price, self.order.get_order_total())

    def test_pay_for_order(self):
        self.order.add_item(item=self.item)
        self.order.pay_for_order()

    def test_payment_fail(self):
        self.order.add_item(item=self.item)
        transaction_id = "Fake Transaction ID"
        self.order.payment_fail(transaction_id)
        self.assertEqual(self.order.payment_status, 'failed')

    def test_payment_success(self):
        transaction_id = "Fake Transaction ID"
        mpesa_id = "FAKE Mpesa ID"
        self.order.add_item(item=self.item)
        order_mpesa_transaction = self.order.payment_success(transaction_id, mpesa_id)
        self.assertIsInstance(
            order_mpesa_transaction,
            OrderMpesaTransaction
        )
