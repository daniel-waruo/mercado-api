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

