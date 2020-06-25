from django.db import models


# Create your models here.
class Buyer(models.Model):
    """Person going to buy the gas
    phone_number - The phone number accessing the platform using USSD
    """
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, null=True)
    location = models.TextField(null=True)

    def __str__(self):
        return "{}({})".format(self.phone_number, self.name)


class ContactQueueManager(models.Manager):
    def add(self, buyer, reason):
        self.create(
            buyer=buyer,
            reason=reason
        )


class ContactQueue(models.Model):
    """Handles queue of user information
    buyer - The customer whose number we have
    reason - Why we are to contact the buyer
    created_at - When created
    processed - Whether the issue has been addressed
    """
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='contacts')
    reason = models.CharField(max_length=200, default="Random")
    created_at = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)

    objects = ContactQueueManager()

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.buyer.phone_number
