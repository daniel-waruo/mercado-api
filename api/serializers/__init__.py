from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import User
from buyers.models import Buyer
from orders.models import Order, OrderItem
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

    order = serializers.PrimaryKeyRelatedField(required=False,queryset=Order.objects.all())

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
