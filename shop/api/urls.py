from api.views import ShopView, ContactView, CategoryView, LoginAccountView, ProductInfoView, \
    BasketView, OrderView, PartherOrders, ConfirmAccount, RegisterAccount
from django.urls import path

urlpatterns = [
    path('users/registrate', RegisterAccount.as_view(), name='registrate'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/shops/', ShopView.as_view(), name='shops'),
    path('user/contact/', ContactView.as_view(), name='contact'),
    path('user/login/', LoginAccountView.as_view(), name='login'),
    path('user/categories/', CategoryView.as_view(), name='category'),
    path('user/product/', ProductInfoView.as_view(), name='product_to_info'),
    path('user/basket/', BasketView.as_view(), name='basket'),
    path('user/orders/', OrderView.as_view(), name='orders'),
    path('shop/orders/', PartherOrders.as_view(), name='shop-orders')

    # path('partner/')s
]