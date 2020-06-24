from django.db import models


# Create your models here.

class ModelManager(models.Manager):
    def get_by_position(self, position: int, queryset=None):
        if queryset is None:
            queryset = self.all()
        return queryset[int(position) - 1]


class Category(models.Model):
    """Category of Items which the item belongs
    Args:
        name - name of category
    """
    name = models.CharField(max_length=200)
    objects = ModelManager()

    def __str__(self):
        return self.name


class Brand(models.Model):
    """Brand to which the Items belongs to
    Args:
        name - name of the brand
        logo - logo of the brand
    """
    name = models.CharField(max_length=200)
    logo = models.URLField()
    objects = ModelManager()

    def __str__(self):
        return self.name


class Item(models.Model):
    """Items to be sold through the USSD platform
    Args:
        name - name of the item
        category  - category where the item belongs e.g gas cylinder, gas burner
        price - price in KES of the item being sold
    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='items')
    brand = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL, related_name='items')
    price = models.DecimalField(decimal_places=2, max_digits=9)
    objects = ModelManager()

    def __str__(self):
        return self.name
