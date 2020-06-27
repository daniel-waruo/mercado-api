from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone
from buyers.models import Buyer, ContactQueue
from dj_africastalking.sms import send_sms
from items.models import Item

vendor_phone = settings.VENDOR['phone']
vendor_name = settings.VENDOR['name']


# Create your models here.
class OrderManager(models.Manager):
    def make_order(self, buyer, item, payment_method='on-delivery'):
        assert payment_method in ['m-pesa', 'on-delivery']
        order = self.create(
            payment_method=payment_method,
            buyer=buyer
        )
        # add item to order
        order.add_item(item)
        # send order requested signal
        order_requested.send(sender=Order, order=order)
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
        """adds an item to the order"""
        return OrderItem.objects.create(
            order=self,
            product=item,
            quantity=quantity
        )

    def get_order_total(self, null=False):
        """ get the total cost for the order """
        total = self.items.all().aggregate(
            Sum('product__price')
        )
        amount_total = total['product__price__sum']
        if not null and amount_total is None:
            raise Exception("No Order Items.Add items to the order")
        return amount_total

    def pay_for_order(self):
        """ function for paying for AfricasTalking Items """
        checkout_request.send(sender=self.__class__, order=self)

    def payment_fail(self, transaction_id):
        self.payment_status = 'failed'
        self.save()
        mpesa_transaction = OrderMpesaTransaction.objects.failed_transaction(
            order=self,
            transaction_id=transaction_id
        )
        # send payment failiure signal
        payment_fail.send(self.__class__, order=self)
        return mpesa_transaction

    def payment_success(self, transaction_id, mpesa_id):
        self.payment_status = 'success'
        self.save()
        mpesa_transaction = OrderMpesaTransaction.objects.successful_transaction(
            order=self,
            transaction_id=transaction_id,
            mpesa_id=mpesa_id,
        )
        payment_success.send(self.__class__, order=self)
        return mpesa_transaction

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
        return "{} {} {} {}".format(self.id, self.buyer.phone_number, self.payment_method, self.payment_status)


class OrderItem(models.Model):
    """Item which was Ordered
    Args:
        order - order which links to the order item.
        product - product which was ordered
        quantity -  number of products which were ordered
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1, "Quantity cannot be less than one")],
                                           default=1)

    class Meta:
        unique_together = ('order', 'product')

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


class OrderCheckout(models.Model):
    """temporary carrier for out checkout requests"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE)


from .receivers import *
