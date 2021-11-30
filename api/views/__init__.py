from rest_framework import viewsets

from api.serializers import ProductSerializer, OrderSerializer, BrandSerializer
from buyers.models import Buyer
from orders.models import Order
from products.models import Product, Category, Brand
from .authentication import login, user
from .metrics import metrics, chart_data, top_five_products, top_five_customers
from ..serializers import CustomerSerializer, CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CustomerViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = self.request.data or {}
        return Buyer.objects.filter(**filters)

    serializer_class = CustomerSerializer


class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = {}
        for key, value in self.request.query_params.items():
            filters[key] = value
        return Order.objects.filter(**filters)

    serializer_class = OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
