from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from api.models import Shop, Category, Contact, Product, ProductInfo, Order
from api.permissions import IsOwnerOrReadOnly
from api.serializers import RegistrateSerializer, ShopSerializer, CategorySerializer, ContactSerializer, \
    ProductSerializer, ProductInfoSerializer, OrderSerializer
from api.utils import generate_unique_username
from shop.settings import EMAIL_HOST_USER


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
            user_id=request.user.id, state='basket').prefetch_related(
            'orderitem_product__product__products_info').annotate(
            total_sum=Sum(F('orderitem_order__quantity') * F('orderitem_product__product__products_info__price'))
        )

        seriralizer = OrderSerializer(basket, many=True)
        return JsonResponse(seriralizer.data, status=200)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)


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

        contact_count = Contact.objects.filter(user= request.user)
        for contact in contact_count:
            contact = get_object_or_404(Contact, user= request.user)
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




