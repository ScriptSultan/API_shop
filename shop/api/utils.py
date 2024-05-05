# from django.contrib.auth.models import User
from typing import Type

from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse

from api.models import Order, User, ConfirmEmailToken
from shop import settings
from shop.settings import EMAIL_HOST_USER


# def generate_unique_username(first_name, last_name):
#     username = f'{first_name}_{last_name}'
#
#     if User.objects.filter(username=username).exists():
#         new_add = 1
#         while User.objects.filter(username=username).exists():
#             new_add += 1
#         username = f"{username}_{new_add}"
#     return username


# def check_auth_user(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)


# def check_auth_and_shop(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'Status': 'False', 'Error': 'Not Log in'}, status=403)
#
#     if not request.user.type != 'shop':
#         return JsonResponse({'Status': 'False', 'Error': 'Только для магазинов'})
@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
     отправляем письмо с подтрердждением почты
    """
    if created and not instance.is_active:
        # send an e-mail to the user
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)

        msg = EmailMultiAlternatives(
            # title:
            f"Password Reset Token for {instance.email}",
            # message:
            token.key,
            # from:
            settings.EMAIL_HOST_USER,
            # to:
            [instance.email]
        )
        msg.send()
def send_order_status_email(user_id):
    user = User.objects.get(id=user_id)
    user_email = user.email
    subject = f'Обновление статуса'
    message = f'Статус вашего заказа изменен на "ЗАКАЗ СФОРМИРОВАН"'
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, sender_email, recipient_list)