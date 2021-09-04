from django.db import models
from orders.models import Order


class Transaction(models.Model):
    merchant_request_id = models.CharField(max_length=64, null=True, unique=True)
    checkout_request_id = models.CharField(max_length=64, null=True, unique=True)
    mpesa_code = models.CharField(max_length=64, null=True, unique=True)
    phone = models.CharField(max_length=30)
    reason_failed = models.TextField(null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    transaction_cost = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    transaction_date = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    TRANSACTION_STATE = (
        ('requested', 'Payment Requested'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('success', 'Success')
    )
    state = models.CharField(choices=TRANSACTION_STATE, max_length=10, default='requested')

    @property
    def is_requested(self):
        return self.state == 'requested'

    @property
    def is_success(self):
        return self.state == 'success'

    @property
    def is_fail(self):
        return self.state == 'failed'

    @property
    def is_pending(self):
        return self.state == 'pending'

    def set_pending(self, merchant_request_id, checkout_request_id):
        self.merchant_request_id = merchant_request_id
        self.checkout_request_id = checkout_request_id
        self.state = 'pending'
        self.save()

    def set_fail(self, merchant_request_id, checkout_request_id, reason_failed):
        self.state = 'failed'
        assert self.checkout_request_id == checkout_request_id
        assert self.merchant_request_id == merchant_request_id
        self.reason_failed = reason_failed
        self.save()

    def set_success(self, **kwargs):
        raise NotImplementedError("Implement set success")

    class Meta:
        abstract = True


class OrderTransactionManager(models.Manager):
    def create(self, amount: float, order: Order, phone: str):
        return super().create(
            amount=amount,
            order=order,
            phone=phone,
        )


class OrderTransaction(Transaction):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    objects = OrderTransactionManager()

    def set_success(self, merchant_request_id, checkout_request_id, mpesa_code):
        self.mpesa_code = mpesa_code
        self.state = 'success'
        assert self.checkout_request_id == checkout_request_id
        assert self.merchant_request_id == merchant_request_id
        self.save()
        # set the order as paid
        self.order.payment_status = 'success'
        self.order.payment_method = 'm-pesa'
        self.order.save()
