from django.db import models
from buyers.models import Buyer
from items.models import Item
from django.core.validators import MinValueValidator


# Create your models here.
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
        ('ship', 'Preparing'),
        ('del', 'Delivered')
    )
    PAYMENT_METHODS = (
        ('m-pesa', 'M-Pesa'),
        ('on-delivery', 'On Delivery')
    )
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=4, choices=STATUS_CHOICES, default='prep')
    payment_status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=15, choices=STATUS_CHOICES, default='on-delivery')

    def __str__(self):
        return self.created_at


class OrderItem(models.Model):
    """ Item which was Ordered
    Args:
        order - order which links to the order item.
        product - product which was ordered
        quantity -  number of products which were ordered
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1, "Quantity cannot be less than one")],
                                           default=1)

    class Meta:
        unique_together = ('order', 'product')

    def __str__(self):
        return self.product.name
