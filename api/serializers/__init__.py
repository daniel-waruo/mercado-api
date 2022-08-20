from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.utils import model_meta

from accounts.models import User
from buyers.models import Buyer
from invoices.models import InvoiceItem, Invoice
from orders.models import Order, OrderItem
from organizations.models import Organization
from products.models import Product, Category, Brand


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            if user.check_password(attrs['password']):
                self.user = user
                return attrs
        except User.DoesNotExist:
            pass
        raise serializers.ValidationError("Invalid Email or Password")

    def save(self, **kwargs):
        return self.user


class CustomerSerializer(serializers.ModelSerializer):
    businessName = serializers.SerializerMethodField('get_business_name')

    def get_business_name(self, buyer: Buyer):
        return buyer.business_name

    class Meta:
        model = Buyer
        fields = '__all__'


class TopCustomerSerializer(CustomerSerializer):
    total_profit = serializers.SerializerMethodField('get_total_profit')

    def get_total_profit(self, buyer: Buyer):
        return buyer.total_profit


class ProductSerializer(serializers.ModelSerializer):
    categoryName = serializers.SerializerMethodField('get_category_name')

    def get_category_name(self, product: Product):
        if product.category:
            return product.category.name

    inStock = serializers.SerializerMethodField('get_in_stock')

    def get_in_stock(self, product: Product):
        return product.in_stock

    class Meta:
        model = Product
        fields = '__all__'


class TopProductSerializer(ProductSerializer):
    total_profit = serializers.SerializerMethodField('get_total_profit')

    def get_total_profit(self, product: Product):
        return product.total_profit

    total_sales = serializers.SerializerMethodField('get_total_sales')

    def get_total_sales(self, product: Product):
        return product.total_sales


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    order = serializers.PrimaryKeyRelatedField(required=False, queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    buyer = CustomerSerializer(read_only=True)

    items = OrderItemSerializer(many=True, read_only=False)

    total = serializers.SerializerMethodField('get_total_amount')

    def get_total_amount(self, order: Order):
        return order.get_order_total()

    def create(self, validated_data):
        items = self.initial_data.pop('items')
        validated_data.pop('items')
        order = Order.objects.create(
            **validated_data,
            buyer_id=self.initial_data.pop('buyer')['id']
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=Product.objects.get(id=item['product']['id']),
                quantity=item['quantity']
            )

        return order

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Order
        fields = '__all__'


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    buyer = CustomerSerializer(read_only=True)

    items = InvoiceItemSerializer(many=True, read_only=False)

    total = serializers.SerializerMethodField('get_total_amount')

    def get_total_amount(self, order: Order):
        return order.get_order_total()

    def create(self, validated_data):
        items = self.initial_data.pop('items')
        validated_data.pop('items')
        invoice = Invoice.objects.create(
            **validated_data,
            buyer_id=self.initial_data.pop('buyer')['id']
        )
        for item in items:
            InvoiceItem.objects.create(
                order=invoice,
                product=Product.objects.get(id=item['product']['id']),
                quantity=item['quantity']
            )

        return invoice

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Order
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
