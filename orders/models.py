from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from buyers.models import Buyer
from products.models import Product
from django.db.models.signals import post_save
from django.dispatch import receiver
from .signals import *


class OrderManager(models.Manager):
    def make_order(self, buyer, item, payment_method='on-delivery', channel="whatsapp"):
        assert payment_method in ['m-pesa', 'on-delivery']
        order = self.create(
            payment_method=payment_method,
            buyer=buyer
        )
        # add item to order
        order.add_item(item)
        # send order requested signal
        order_requested.send(sender=Order, order=order, channel=channel)
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


class OrderItem(models.Model):
    """Product which was Ordered
    Args:
        order - order which links to the order item.
        product - product which was ordered
        quantity -  number of products which were ordered
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ordered_items')
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Quantity cannot be less than one")],
        default=1
    )

    class Meta:
        unique_together = (('order', 'product'),)

    def __str__(self):
        return self.product.name


@receiver(post_save, sender=Order)
def order_signals(sender, instance: Order, created: bool, **kwargs):
    # get current order
    order = Order.objects.get(id=instance.id)
    if created:
        # send order requested signal
        order_requested.send(sender=sender, order=order, channel=order.channel)

    if instance.status == "ship" and order.status != "ship":
        # send order shipping signal
        order_shipping.send(sender=sender, order=order)

    if instance.status == "can" and order.status != "can":
        # send order cancelled signal
        order_cancel.send(sender=sender, order=order)

    if instance.status == "fin" and order.status != "fin":
        # send order delivered signal
        order_delivered.send(sender=sender, order=order)
