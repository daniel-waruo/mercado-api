from django.db import models


# Create your models here.
from organizations.models import Organization


class Buyer(models.Model):
    """
    Person going to buy the gas
        phone_number - The phone number accessing the platform using sms
        name - The name of the buyer
        The location of the buyer
    """
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, null=True)
    location = models.TextField(null=True)
    business_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, related_name='buyers')

    def __str__(self):
        return "{}({})".format(self.phone, self.name)


class Message(models.Model):
    message_id = models.CharField(max_length=72, unique=True)
