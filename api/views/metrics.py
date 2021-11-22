from datetime import timedelta

from django.db.models import DecimalField, Q
from django.db.models import Sum, F, Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response

from api.serializers import TopCustomerSerializer, TopProductSerializer
from buyers.models import Buyer
from orders.models import Order, OrderItem
from products.models import Product


class MetricsViewSet(viewsets.ViewSet):

    def metrics(self, request):
        totals = OrderItem.objects.filter(
            order__status='fin',
            order__payment_status='success'
        ).aggregate(
            total_profits=Sum(F('price') - F('cost'), output_field=DecimalField()),
            total_cost=Sum(F('cost'), output_field=DecimalField()),
            total_revenue=Sum(F('price'), output_field=DecimalField()),
        )
        members_online = Buyer.objects.filter(
            sessions__updated_at__gt=timezone.now() - timedelta(minutes=5)
        ).count()
        today_revenue = OrderItem.objects.filter(
            order__created_at__gt=timezone.now() - timedelta(days=1),
            order__status='fin',
        ).aggregate(
            today_revenue=Sum(F('price')),
        )
        return Response(
            status=200,
            data={
                'message': 'Fetched Metrics',
                'success': True,
                'data': {
                    'totalSales': Order.objects.filter(status='fin').count(),
                    'totalCustomers': Buyer.objects.count(),
                    'totalProfits': totals.get('total_profits') or 0,
                    'totalCost': totals.get('total_cost') or 0,
                    'membersOnline': members_online,
                    'todayRevenue': today_revenue.get('today_revenue') or 0,
                    'totalRevenue': totals.get('total_revenue') or 0,
                }
            }
        )

    def chart_data(self, request, year):
        return Response(
            status=200,
            data={
                'message': 'Fetched Chart Data',
                'success': True,
                'data': OrderItem.objects.year_metrics(year)
            }
        )

    def top_five_customers(self, request):
        buyers = Buyer.objects.filter(
            orders__status='fin',
        ).annotate(
            total_profit=Sum(F('orders__items__price') - F('orders__items__cost'), output_field=DecimalField())
        ).order_by('total_profit')
        return Response(
            status=200,
            data={
                'message': 'Fetched Top 5 Customers',
                'success': True,
                'data': TopCustomerSerializer(instance=buyers, many=True).data
            }
        )

    def top_five_products(self, request):
        products = Product.objects.filter(
            ordered_items__order__status='fin'
        ).annotate(
            total_profit=Sum(F('ordered_items__price') - F('ordered_items__cost'), output_field=DecimalField()),
            total_sales=Count('ordered_items')
        ).order_by('-total_profit')
        return Response(
            status=200,
            data={
                'message': 'Fetched Top 5 Products',
                'success': True,
                'data': TopProductSerializer(
                    instance=products,
                    many=True
                ).data
            }
        )

    def order_metrics(self, request):
        totals = Order.objects.aggregate(
            total_orders=Count('id', filter=Q(
                status='fin',
                payment_status='success'
            )),
            total_amount=Sum('items__product__price', filter=Q(
                status='fin',
                payment_status='success'
            )),
            total_cancelled=Count('id', filter=Q(status='can')),
            all_count=Count('id')
        )
        total_amount = totals['total_amount'] or 0
        total_orders = totals['total_orders'] or 0
        total_cancelled = totals['total_cancelled'] or 0
        all_count = totals['all_count'] or 0

        if total_amount == 0 or total_orders == 0:
            avg_order_value = 0
        else:
            avg_order_value = round(total_amount / total_orders, 2)

        if total_cancelled == 0 or all_count == 0:
            order_cancel_rate = 0
        else:
            order_cancel_rate = round((total_cancelled / all_count) * 100, 2)

        return Response(
            status=200,
            data={
                'message': 'Fetched Metrics',
                'success': True,
                'data': {
                    'totalOrders': total_orders,
                    'avgOrderValue': avg_order_value,
                    'orderCancelRate': order_cancel_rate
                }
            }
        )

    def customer_metrics(self, request):
        totals = Buyer.objects.aggregate(
            total_customers=Count('id'),
        )

        return Response(
            status=200,
            data={
                'message': 'Fetched Metrics',
                'success': True,
                'data': {
                    'totalCustomer': totals['total_customer'] or 0,
                    'avgCustomerRevenue': 0,
                    'conversionRate': 0
                }
            }
        )

    def inventory_metrics(self, request):
        totals = Product.objects.aggregate(
            total_orders=Count('id', filter=Q(
                status='fin',
                payment_status='success'
            )),
            total_amount=Sum('items__product__price', filter=Q(
                status='fin',
                payment_status='success'
            )),
            total_cancelled=Count('id', filter=Q(status='can')),
            all_count=Count('id')
        )
        return Response(
            status=200,
            data={
                'message': 'Fetched Metrics',
                'success': True,
                'data': {
                    'totalProducts': totals['total_orderdavbzdz'],
                }
            }
        )


customer_metrics = MetricsViewSet.as_view({'get': 'customer_metrics'})
order_metrics = MetricsViewSet.as_view({'get': 'order_metrics'})
metrics = MetricsViewSet.as_view({'get': 'metrics'})
chart_data = MetricsViewSet.as_view({'get': 'chart_data'})
top_five_customers = MetricsViewSet.as_view({'get': 'top_five_customers'})
top_five_products = MetricsViewSet.as_view({'get': 'top_five_products'})
