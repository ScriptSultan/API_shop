from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from api.models import Category, Shop, Product, ProductParameter, ProductInfo, Parameter, Order, OrderItem, Contact
from api.utils import generate_unique_username


class RegistrateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'password'
        )

    def validate_email(self, value):
        # email = value.get('email')
        if User.objects.filter(email=value).exists(): # сломано
            raise ParseError('Пользователь зарегистрирован')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if first_name and last_name:
            username = generate_unique_username(first_name, last_name)
            data['username'] = username
        return data


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category')


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value')


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    name = serializers.StringRelatedField()
    quantity = serializers.IntegerField()
    price = serializers.IntegerField()

    class Meta:
        model = ProductInfo
        fields = ('name', 'quantity', 'price')


class ParameterSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()

    class Meta:
        model = Parameter
        fields = ('name',)


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order


class OrderItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ('quantity',)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ('type_contact', 'user', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')
        extra_kwargs = {
            'type_contact': {'required': False},
            'user': {'required': False}
        }
