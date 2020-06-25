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
    def make_order(self, buyer, item, on_delivery=True):
        extra_kwargs = {}
        if not on_delivery:
            extra_kwargs = {
                'payment_method': 'm-pesa'
            }
        order = self.create(buyer=buyer, **extra_kwargs)
        order.add_item(item)
        if on_delivery:
            ContactQueue.objects.add(buyer, reason="Ordered A Delivery.Get Location")
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
        return OrderItem.objects.create(
            order=self,
            product=item,
            quantity=quantity
        )

    def get_order_total(self, null=False):
        total = self.items.all().aggregate(
            Sum('product__price')
        )
        amount_total = total['product__price__sum']
        if not null and amount_total is None:
            raise Exception("No Order Items.Add items to the order")
        return amount_total

    def pay_for_order(self):
        """ function for paying for AfricasTalking Items """
        product_name = settings.AFRICASTALKING['product_name']
        total_amount = float(self.get_order_total())
        checkout_request.send(sender=self, buyer=self.buyer)

    def payment_fail(self):
        self.payment_status = 'failed'
        self.save()
        send_sms(
            self.buyer.phone_number,
            render_to_string(
                'sms/payment_success.txt',
                context={
                    'buyer': self.buyer,
                    'order': self
                }
            )
        )
        ContactQueue.objects.add(self.buyer, reason="Payment Failed")

    def payment_success(self, transaction_id):
        self.payment_status = 'success'
        self.save()
        OrderMpesaTransaction.objects.create(
            order=self,
            transaction_id=transaction_id
        )
        send_sms(
            self.buyer.phone_number,
            render_to_string(
                'sms/payment_success.txt',
                context={
                    'buyer': self.buyer,
                    'order': self
                }
            )
        )
        ContactQueue.objects.add(self.buyer, reason="Paid Successfully and Ordered Goods.Get Location")
        return OrderMpesaTransaction.objects.create(
            order=self,
            transaction_id=transaction_id
        )

    def ship_order(self):
        self.status = 'ship'
        self.save()
        delivery_start = timezone.datetime.now() + timezone.timedelta(minutes=30)
        delivery_end = timezone.datetime.now() + timezone.timedelta(hours=1)
        send_sms(
            self.buyer.phone_number,
            render_to_string(
                'sms/order_shipping.txt',
                context={
                    'buyer': self.buyer,
                    'order': self,
                    'delivery_start': delivery_start,
                    'delivery_end': delivery_end
                }
            )
        )

    def cancel_order(self):
        self.status = 'can'
        self.save()
        send_sms(
            self.buyer.phone_number,
            render_to_string(
                'sms/order_cancel.txt',
                context={
                    'buyer': self.buyer,
                    'order': self,
                }
            )
        )
        ContactQueue.objects.add(self.buyer, reason="Cancelled Order")

    def finish_order(self):
        self.status = 'can'
        self.save()
        ContactQueue.objects.add(buyer=self.buyer, reason="Finished Order Get Feed Back")

    def __str__(self):
        return "order by {} time - {}".format(self.buyer.phone_number,
                                              self.created_at.strftime('%I:%M %p on the %d of %B %Y'))


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


class OrderMpesaTransaction(models.Model):
    """This maps all our orders paid by m-pesa
     Args:
         transaction_id - The mpesa transaction code provided by safaricom
         order - The order mapped on this transaction
     """
    transaction_id = models.CharField(max_length=200, primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='transaction')

    # africastalking_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.transaction_id


class OrderCheckout(models.Model):
    """temporary carrier for out checkout requests"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE)


from .receivers import *
