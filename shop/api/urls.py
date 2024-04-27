from api.views import RegistrateView, ShopView, ContactView, CategoryView, LoginAccountView, ProductInfoView, BasketView
from django.urls import path

urlpatterns = [
    path('users/registrate', RegistrateView.as_view(), name='registrate'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('user/contact/', ContactView.as_view(), name='contact'),
    path('user/login/', LoginAccountView.as_view(), name='login'),
    path('categories/', CategoryView.as_view(), name='category'),
    path('user/shop/<int:shop_id>', ProductInfoView.as_view(), name='shop_to_info'),
    path('user/product/<int:product_id>', ProductInfoView.as_view(), name='product_to_info'),
    path('user/basket/', BasketView.as_view(), name='basket'),
]