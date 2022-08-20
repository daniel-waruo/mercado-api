from django.contrib.auth.models import AbstractUser
from django.db import models

from organizations.models import Organization


class User(AbstractUser):
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, related_name='users')


class Vendor(models.Model):
    phone = models.CharField(max_length=20)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()
