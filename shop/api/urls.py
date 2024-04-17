from api.views import RegistrateView, ShopView, ContactView, CategoryView, LoginAccountView
from django.urls import path

urlpatterns = [
    path('users/registrate', RegistrateView.as_view(), name='registrate'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('user/contact/', ContactView.as_view(), name='contact'),
    path('user/login/', LoginAccountView.as_view(), name='login'),
    path('categories/', CategoryView.as_view(), name='category'),
]