from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, F

from buyers.models import Buyer
from orders.models import Order
from organizations.models import Organization
from products.models import Product
from .signals import *


class InvoiceManager(models.Manager):
    def make_invoice(self,
                     buyer,
                     item,
                     payment_method='on-delivery',
                     channel="whatsapp", quantity=1, store=None,
                     send_signal=True):
        assert payment_method in ['m-pesa', 'on-delivery']
        order = self.create(
            payment_method=payment_method,
            buyer=buyer
        )

        # add item to order
        order.add_item(item, quantity)
        # send order requested signal
        order_requested.send(sender=Invoice, order=order, store=store, channel=channel, send_signal=send_signal)
        return order

    def make_invoice_from_order(self, order: Order):
        pass

class Invoice(models.Model):

    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, related_name='invoices')

    PAYMENT_STATUS = (
        ('success', 'Successful Payment'),
        ('failed', 'Payment Failed'),
        ('cancelled', 'Payment Cancelled'),
        ('pending', 'Payment Pending')
    )
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')

    payment_method = models.CharField(max_length=50, null=True)
    payment_proof = models.FileField(upload_to='payment_proofs', null=True)
    transaction_id = models.CharField(max_length=50, null=True)

    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, related_name='invoices')

    objects = InvoiceManager()

    class Meta:
        ordering = '-id',

    def add_item(self, item, quantity=1):
        """ adds an item to the order"""
        return InvoiceItem.objects.create(
            invoice=self,
            product=item,
            quantity=quantity
        )

    def get_total(self, null=True):
        """ get the total cost for the order """
        amount = self.items.all().aggregate(
            total=Sum(F('price') * F('quantity')),
        )['total'] or 0
        if not null and amount == 0:
            raise Exception(f"No Invoice Items for Invoice {self.id}.Add products to the invoice")
        return amount

    def invoice_success(self):
        self.status = 'success'
        self.save()

    def invoice_failed(self):
        self.payment_status = 'failed'
        self.save()

    def invoice_cancelled(self, transaction_id, mpesa_id):
        self.payment_status = 'cancelled'
        self.save()

    def __str__(self):
        return f"Invoice No. {self.id}"


class InvoiceItemManager(models.Manager):
    def create(self, invoice, product, quantity):
        return super().create(
            invoice=invoice,
            product=product,
            quantity=quantity,
            item_name=product.name,
            price=product.price,
            cost=product.cost
        )


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='invoiced_items')
    item_name = models.TextField(null=True)
    price = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    cost = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Quantity cannot be less than one")],
        default=1
    )

    objects = InvoiceItemManager()

    class Meta:
        unique_together = (('invoice', 'product'),)

    def __str__(self):
        return self.item_name
