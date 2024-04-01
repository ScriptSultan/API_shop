from shop.api.views import RegistrateView
from django.urls import path

urlpatterns = [
    path('users/registrate', RegistrateView.as_view(), name='registrate')
]