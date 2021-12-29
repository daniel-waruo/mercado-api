import calendar

from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, Q, F
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from buyers.models import Buyer
from products.models import Product
from store.models import StoreOrder
from .signals import *
from .utils import months


class OrderManager(models.Manager):
    def make_order(self, buyer, item, payment_method='on-delivery', channel="whatsapp", quantity=1, store=None):
        assert payment_method in ['m-pesa', 'on-delivery']
        order = self.create(
            payment_method=payment_method,
            buyer=buyer
        )
        # add item to order
        order.add_item(item, quantity)
        if store:
            StoreOrder.objects.create(store=store, order=order)
        # send order requested signal
        order_requested.send(sender=Order, order=order, store=store, channel=channel)
        return order


class Order(models.Model):
    """ Manages Orders of the Items
    Args:
        STATUS_CHOICES - this is the status of the delivery during the delivery process
        PAYMENT_METHODS - these are the different payment methods that one can use to pay
        buyer - the person who buys the order
        created_at - the time at which the order was made
        status - maintains the different states of the order
        payment_status -  boolean value to tell us whether the good was paid or not
        payment_method - mode by which the payment was made.
    """
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, related_name='orders')

    STATUS_CHOICES = (
        ('prep', 'Preparing'),
        ('ship', 'On Transit'),
        ('fin', 'Delivery Finished'),
        ('can', 'Delivery Cancelled')
    )
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='prep')

    PAYMENT_STATUS = (
        ('success', 'Successful Payment'),
        ('failed', 'Payment Failed '),
        ('pending', 'Payment Pending ')
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')

    PAYMENT_METHODS = (
        ('m-pesa', 'M-Pesa'),
        ('on-delivery', 'On Delivery')
    )
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, default='on-delivery')

    CHANNEL = (
        ('ussd', 'USSD'),
        ('sms', 'SMS'),
        ('whatsapp', 'Whatsapp')
    )
    channel = models.CharField(max_length=15, choices=CHANNEL, default='whatsapp')

    created_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        ordering = '-id',

    def add_item(self, item, quantity=1):
        """ adds an item to the order"""
        return OrderItem.objects.create(
            order=self,
            product=item,
            quantity=quantity
        )

    def get_order_total(self, null=False):
        """ get the total cost for the order """
        amount = self.items.all().aggregate(
            Sum('product__price')
        )['product__price__sum'] or 0
        if not null and amount == 0:
            raise Exception("No Order Items.Add products to the order")
        return amount

    def ship_order(self):
        self.status = 'ship'
        self.save()

    def cancel_order(self):
        self.status = 'can'
        self.save()

    def finish_order(self):
        self.status = 'fin'
        self.save()

    def payment_fail(self):
        self.payment_status = 'failed'
        self.save()

    def payment_success(self, transaction_id, mpesa_id):
        self.payment_status = 'success'
        self.save()

    def __str__(self):
        return f"Order No. {self.id}"


class OrderItemManager(models.Manager):
    def create(self, order, product, quantity):
        return super().create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
            cost=product.cost
        )

    def year_metrics(self, year: int):
        start, end = timezone.datetime(year, 1, 1), timezone.datetime(year, 12, 31)
        qs = self.get_queryset()
        sales_aggregations = {}
        profit_aggregations = {}
        for month in months(start, end):  # the start of each month in the range
            month_name = calendar.month_name[month.month]
            aggregation_name = month_name
            profit_aggregations[aggregation_name] = Sum(
                F('price') - F('cost'), filter=Q(
                    order__status='fin',
                    order__payment_status='success',
                    order__created_at__gt=month,
                    order__created_at__lte=month + relativedelta(months=1)
                )
            )
            sales_aggregations[aggregation_name] = Sum(
                'quantity', filter=Q(
                    order__status='fin',
                    order__payment_status='success',
                    order__created_at__gt=month,
                    order__created_at__lte=month + relativedelta(months=1)
                )
            )
        return {
            'profit': list(map(lambda item: item[1] or 0, qs.aggregate(**profit_aggregations).items())),
            'sales': list(map(lambda item: item[1] or 0, qs.aggregate(**sales_aggregations).items()))
        }


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ordered_items')
    price = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    cost = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Quantity cannot be less than one")],
        default=1
    )

    objects = OrderItemManager()

    class Meta:
        unique_together = (('order', 'product'),)

    def __str__(self):
        return self.product.name


def state_to_ord(status):
    if 'prep' == status:
        return 1
    if 'ship' == status:
        return 2
    if 'fin' == status:
        return 3
    if 'can' == status:
        return 4


@receiver(pre_save, sender=Order)
def order_signals(sender, instance: Order, raw, **kwargs):
    # get current order
    order = Order.objects.get(id=instance.id)
    order_level = state_to_ord(order.status)
    print(kwargs)
    if instance.status == "ship" and order_level == 1:
        # send order shipping signal
        order_shipping.send(sender=sender, order=instance)

    elif instance.status == "fin" and order_level <= 2:
        # send order delivered signal
        order_delivered.send(sender=sender, order=instance)

    elif instance.status == "can" and order_level <= 2:
        # send order cancelled signal
        order_cancel.send(sender=sender, order=instance)
