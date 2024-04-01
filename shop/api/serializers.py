from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ParseError


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
        email = value.get('email')
        if User.objects.filter(email=email).exists():
            raise ParseError('Пользователь зарегистрирован')
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

