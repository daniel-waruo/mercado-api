from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

from buyers.models import Buyer
from products.models import Product


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
    """Manages Orders of the Items
    Args:
        STATUS_CHOICES - this is the status of the delivery during the delivery process
        PAYMENT_METHODS - these are the different payment methods that one can use to pay
        buyer - the person who buys the order
        created_at - the time at which the order was made
        status - maintains the different states of the order
        payment_status -  boolean value to tell us whether the good was paid or not
        payment_method - mode by which the payment was made.
    """
    STATUS_CHOICES = (
        ('prep', 'Preparing'),
        ('ship', 'On Transit'),
        ('fin', 'Delivery Finished'),
        ('can', 'Delivery Cancelled')
    )
    PAYMENT_METHODS = (
        ('m-pesa', 'M-Pesa'),
        ('on-delivery', 'On Delivery')
    )
    PAYMENT_STATUS = (
        ('success', 'Successful Payment'),
        ('failed', 'Payment Failed '),
        ('pending', 'Payment Pending ')
    )
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='prep')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS, default='on-delivery')
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

    def payment_fail(self):
        self.payment_status = 'failed'
        self.save()

    def payment_success(self, transaction_id, mpesa_id):
        self.payment_status = 'success'
        self.save()

    def ship_order(self):
        self.status = 'ship'
        self.save()
        # send order shipping signal
        order_shipping.send(self.__class__, order=self)

    def cancel_order(self):
        self.status = 'can'
        self.save()
        # send order cancelled signal
        order_cancel.send(self.__class__, order=self)

    def finish_order(self):
        self.status = 'can'
        self.save()
        # send order delivered signal
        order_delivered.send(self.__class__, order=self)

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


class OrderMpesaTransactionManager(models.Manager):
    def successful_transaction(self, order, transaction_id, mpesa_id):
        return self.create(
            order=order,
            transaction_id=transaction_id,
            mpesa_transaction_id=mpesa_id,
            status='success'
        )

    def failed_transaction(self, order, transaction_id):
        return self.create(
            order=order,
            transaction_id=transaction_id
        )


class OrderMpesaTransaction(models.Model):
    """This maps all our orders paid by m-pesa
     Args:
         mpesa_transaction_id - The code provided by safaricom
         transaction_id - The transaction id provided by africastalking
         order - The order mapped on this transaction
     """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='transaction', editable=False)
    transaction_id = models.CharField(max_length=200, primary_key=True, editable=False, unique=True)
    mpesa_transaction_id = models.CharField(max_length=200, null=True, editable=False, unique=True)

    STATUS = (
        ('success', 'Success'),
        ('failed', 'Failed')
    )
    status = models.CharField(max_length=10, choices=STATUS, default='failed', editable=False)

    objects = OrderMpesaTransactionManager()

    def __str__(self):
        return self.transaction_id


# import signal receivers
from .receivers import *
