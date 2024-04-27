import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from api.models import Shop, Category, Contact, Product, ProductInfo, Order
from api.permissions import IsOwnerOrReadOnly
from api.serializers import RegistrateSerializer, ShopSerializer, CategorySerializer, ContactSerializer, \
    ProductSerializer, ProductInfoSerializer, OrderSerializer, OrderItemSerializer
from api.utils import generate_unique_username
from shop.settings import EMAIL_HOST_USER
from ujson import loads as load_json
from django.db import IntegrityError

class RegistrateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrateSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = default_token_generator.make_token(user)
        token_record = Token.objects.create(user=user, key=token)
        token_record.save()
        self.send_token_email(user.email, token)

    def send_token_email(self, user_email, token):
        subject = 'Ваш токен для доступа к API'
        message = f'Ваш токен: {token}'
        sender_email = EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, sender_email, recipient_list)


class LoginAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, **kwargs)

            if user is True and user.is_active:
                token = Token.objects.get(user=user)
                return JsonResponse({'Status': 'True', 'Token': token.key})

            return JsonResponse({'Status': 'False', 'Error': "Invalid data"})

        return JsonResponse({'Status': 'False', 'Error': 'Не указаны аргументы'})


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

"""НУЖНЫ ЛИ ТУТ ФИЛЬТРЫ?"""
class ProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_class = ...


class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = ProductInfo.objects.filter(shop__state=True)
        shop_id = request.get('shop_id')
        product_id = request.get('product_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        queryset = queryset.select_related(
            'shop', 'product__category').prefetch_related(
            'product_details__parameter').distinct()
        serializer = ProductInfoSerializer(queryset, many=True)
        return JsonResponse(serializer.data)


'''ДОДЕЛАТЬ'''
class BasketView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'orderitem_order__product__products_info').annotate(
            total_sum=Sum(F('orderitem_order__quantity') * F('orderitem_order__product__products_info__price'))
        )

        seriralizer = OrderSerializer(basket, many=True)
        # print('================================================================')
        # print(seriralizer.data)
        return JsonResponse(seriralizer.data, safe=False)
        # 'TypeError: In order to allow non-dict objects to be serialized set the safe parameter to False.'
    def post(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        try:
            items_data = json.loads(request.body).get('items')
        except json.JSONDecodeError:
            return JsonResponse({'Status': False, 'Error': 'Invalid JSON format'}, status=400)

        if not items_data:
            return JsonResponse({'status': False, 'error': 'No item data provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            basket, _ = Order.objects.get_or_create(user=request.user, status='basket')
        except Order.MultipleObjectsReturned:
            return JsonResponse({'status': False, "error": 'Basket already exists'})
        except IntegrityError as error:
            return JsonResponse({'status': False, 'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # print(items_data)
        objects_created = 0
        for item_data in items_data:
            print(item_data)
            print(basket.id)
            item_data['order'] = basket.id
            print(item_data)
            serializer = OrderItemSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save(order=basket)
                objects_created += 1
            else:
                return JsonResponse({'status': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        print(objects_created)
        return JsonResponse({'status': True, 'objects_created': objects_created}, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        items_data = json.loads(request.body).get('items')
        if not items_data:
            return JsonResponse({'status': False, 'error': 'No item data provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            basket, _ = Order.objects.get_or_create(user=request.user, status='basket')
        except IntegrityError as error:
            return JsonResponse({'status': False, 'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        objects_update = 0
        for item_data in items_data:
            print(basket)
            item_data['order_id'] = basket.id
            serializer = OrderItemSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                objects_update += 1
            else:
                objects_update += 1

        return JsonResponse({'Status': True, 'Создано объектов': objects_update})



    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        items_data = request.data.get('items')
        basket = None
        if not items_data:
            return JsonResponse({'status': False, 'error': 'No item data provided'}, status=status.HTTP_400_BAD_REQUEST)
        basket = Order.objects.get_or_create(user_id=request.user.id, status='basket')
        objects_deleted = False
        query = Q()
        for item_data in items_data:
            query = query | Q(order_id=basket.id, id=item_data)

class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        contact = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contact, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        if {'city', 'street', 'house', 'phone'}.issubset(request.data):
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(user=request.user)
                return JsonResponse({'success': True}, status=201)
            else:
                return JsonResponse({'success': False, 'errors': serializer.errors}, status=400)
        else:
            return JsonResponse({'success': False, 'Error': 'missed args'}, status=403)

    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        contact_count = Contact.objects.filter(user=request.user)
        for contact in contact_count:
            contact = get_object_or_404(Contact, user=request.user)
            contact_serializer = ContactSerializer(contact, data=request.data, partial=True)
            if contact_serializer.is_valid():
                contact_serializer.save()
                return JsonResponse({'Status': 'True'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

        user = request.user
        contacts = Contact.objects.filter(user=user)

        if contacts.exists():
            contact = contacts.first()
            contact.delete()
            return JsonResponse({'Status': 'True'}, status=200)
        else:
            return JsonResponse({'Status': 'False', 'Error': 'No contacts found for the current user'}, status=404)




