from accounts.models import User
from django.db import models

from products.models import Product


class Store(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_products')


class StoreOrder(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='store_orders')

    def __str__(self):
        return str(self.order)
