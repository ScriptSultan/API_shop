from django.contrib.auth.models import User


def generate_unique_username(first_name, last_name):
    username = f'{first_name}_{last_name}'

    if User.objects.filter(username=username).exists():
        new_add = 1
        while User.objects.filter(username=username).exists():
            new_add += 1
        username = f"{username}_{new_add}"
    return username
