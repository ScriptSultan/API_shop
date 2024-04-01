from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from api.serializers import RegistrateSerializer


class RegistrateView(CreateAPIView):
    queryset = User.objects.all()
    serializer = RegistrateSerializer


