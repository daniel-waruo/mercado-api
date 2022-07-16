from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.serializers import ProductSerializer, OrderSerializer, BrandSerializer, InvoiceSerializer
from buyers.models import Buyer
from invoices.models import Invoice
from orders.models import Order
from products.models import Product, Category, Brand
from .authentication import login, user
from .metrics import metrics, chart_data, top_five_products, top_five_customers
from ..serializers import CustomerSerializer, CategorySerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    authentication_classes = [TokenAuthentication]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query')
        return Product.objects.filter(
            name=query,
            description=query
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            **request.data,
            "user": request.user.id
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CustomerViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = {}
        for key, value in self.request.query_params.items():
            if key != "page":
                filters[key] = value
        return Buyer.objects.filter(**filters).order_by('id')

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


class InvoiceViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        # get all query parameters and place them in
        # the query params
        filters = {}
        for key, value in self.request.query_params.items():
            if key != "page":
                filters[key] = value
        return Invoice.objects.filter(**filters)


class CategoryViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
