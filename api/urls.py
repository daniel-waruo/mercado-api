from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from api.views import ProductViewSet, OrderViewSet, CustomerViewSet, CategoryViewSet, BrandViewSet
from api.views import (
    login, user, metrics,
    chart_data, top_five_products, top_five_customers,
)
from api.views.metrics import (
    order_metrics,
    customer_metrics,
    inventory_metrics
)

urlpatterns = [
    # login and all pages
    path('login', csrf_exempt(login)),
    path('user', user),

    # dashboard page
    path('metrics', metrics),
    path('chart-data/<int:year>', chart_data),
    path('top-five-products', top_five_products),
    path('top-five-customers', top_five_customers),

    # order page
    path('order-metrics', order_metrics),
    # customer page
    path('customer-metrics', customer_metrics),
    # inventory page
    path('inventory-metrics', inventory_metrics),
]

router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')

urlpatterns += router.urls
