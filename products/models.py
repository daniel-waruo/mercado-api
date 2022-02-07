from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


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
        ordering = 'name',
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

    class Meta:
        ordering = 'name',

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product to be sold through the USSD platform
    Args:
        sku - unique identifier of the product
        name - name of the item
        description - description of the product
        category  - category where the item belongs e.g gas cylinder, gas burner
        brand - The brand of the product
        tag - identifier of the product used for analytics
        product_code - code for use in USSD or promotions
        price - price of the product
        cost - cost of the product
        in_stock - check if product is in stock
    """
    sku = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    image = models.ImageField(null=True, upload_to='product_images')
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='products')
    brand = models.ForeignKey(Brand, null=True, on_delete=models.SET_NULL, related_name='products')

    tag = models.CharField(max_length=50, null=True)

    product_code = models.CharField(max_length=50, null=True)

    price = models.DecimalField(decimal_places=2, max_digits=9)
    cost = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)

    active = models.BooleanField(default=True)

    in_stock = models.PositiveIntegerField(default=0)

    objects = ModelManager()

    class Meta:
        ordering = 'sku',

    def __str__(self):
        return self.name


@receiver(post_save, sender=Product)
def facebook_update(sender, instance: Product, raw, **kwargs):
    pass
