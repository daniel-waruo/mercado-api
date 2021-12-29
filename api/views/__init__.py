from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from api.serializers import ProductSerializer, OrderSerializer, BrandSerializer
from buyers.models import Buyer
from orders.models import Order
from products.models import Product, Category, Brand
from .authentication import login, user
from .metrics import metrics, chart_data, top_five_products, top_five_customers
from ..serializers import CustomerSerializer, CategorySerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = {}
        for key, value in self.request.query_params.items():
            if key != "page":
                filters[key] = value
        return Buyer.objects.filter(**filters)

    serializer_class = CustomerSerializer


class OrderViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = {}
        for key, value in self.request.query_params.items():
            if key != "page":
                filters[key] = value
        return Order.objects.filter(**filters)

    serializer_class = OrderSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
