from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from api.models import Shop, Category, Contact
from api.permissions import IsOwnerOrReadOnly
from api.serializers import RegistrateSerializer, ShopSerializer, CategorySerializer, ContactSerializer
from api.utils import generate_unique_username
from shop.settings import EMAIL_HOST_USER


class RegistrateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrateSerializer

    def perform_create(self, serializer):
        print(serializer)
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


# class ShopView(APIView):
    # permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    #
    # def post(self, request):
    #     serializer = ShopSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'Shop created': 'OK'}, status=201)
    #     else:
    #         return Response(serializer.errors, status=400)
    #
    # def get(self, request):
    #     shop = Shop.objects.all()
    #     serializer = ShopSerializer(shop, many=True)
    #     return JsonResponse(serializer.data)
    #
    # def patch(self, request, pk):
    #     shop = None
    #     if Shop.objects.get(pk=pk):
    #         shop = Shop.objects.get(pk=pk)
    #     else:
    #         raise NotFound('Shop not found')
    #
    #     serializer = ShopSerializer(shop, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'message': 'Shop updated'}, status=200)
    #     else:
    #         return Response({'message': 'Shop not found'}, status=400)
    #
    # def delete(self, request, pk):
    #     shop = None
    #     if Shop.objects.get(pk=pk):
    #         shop = Shop.objects.get(pk=pk)
    #     else:
    #         raise NotFound('Shop not found')
    #
    #     shop.delete()
    #     return Response({'message': 'Shop deleted'}, status=204)


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class ProductView(APIView):
    def get(self, request):
        pass
    def post(self, request):
        pass

    def patch(self, request):
        pass

    def delete(self, request):
        pass


class ProductInfoView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass

    def patch(self, request):
        pass

    def delete(self, request):
        pass


class ParameterView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass

    def patch(self, request):
        pass

    def delete(self, request):
        pass


class ProductParameterView(APIView):
    pass


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
            user = request.user
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(user=request.user)
                return JsonResponse({'success': True}, status=201)
            else:
                print(serializer.errors)
                return JsonResponse({'success': False, 'errors': serializer.errors}, status=400)
        else:
            return JsonResponse({'success': False, 'Error': 'missed args'}, status=403)

    def patch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)
        user = request.user
        print(request.data)
        contact_count = Contact.objects.filter(user=user)
        for contact in contact_count:
            print(contact.phone)
        contact = get_object_or_404(Contact, user=user)
        print(contact)
        contact_serializer = ContactSerializer(contact, data=request.data, partial=True)
        # contact.update(request.data)
        if contact_serializer.is_valid():
            contact_serializer.save()
            return JsonResponse({'Status': 'True'})
        # return JsonResponse({'Status': 'True'}, status=200)

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






class OrderView(APIView):
    pass


class OrderItemView(APIView):
    pass



