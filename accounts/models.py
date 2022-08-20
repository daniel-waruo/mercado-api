from django.contrib.auth.models import AbstractUser
from django.db import models

from organizations.models import Organization


class Role(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, related_name='users')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, related_name='users')


class Vendor(models.Model):
    phone = models.CharField(max_length=20)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()
