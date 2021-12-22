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

    class Meta:
        verbose_name_plural = "categories"


class Brand(models.Model):
    """Brand to which the Items belongs to
    Args:
        name - name of the brand
        logo - logo of the brand
    """
    name = models.CharField(max_length=200)
    logo = models.URLField(null=True)
    objects = ModelManager()

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product to be sold through the USSD platform
    Args:
        name - name of the item
        category  - category where the item belongs e.g gas cylinder, gas burner
        brand - The brand of the product
        price - price of the product
    """
    sku = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)

    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='products')
    brand = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL, related_name='products')

    tag = models.CharField(max_length=50, null=True)

    product_code = models.CharField(max_length=50, null=True)

    price = models.DecimalField(decimal_places=2, max_digits=9)
    cost = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)

    in_stock = models.PositiveIntegerField(default=0)

    objects = ModelManager()

    def __str__(self):
        return self.name
