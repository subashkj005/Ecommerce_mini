from django.urls import path
from .views import *
from cart.views import *


urlpatterns = [
    path('', homepage, name='user_home'),
    path('product<int:id>', productpage, name='product_page'),
    path('test', test_page, name='test_page'),
    path('profile', profile_page, name='profile_page'),
    path('cart', cart_page, name='cart_page'),
    path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
    path('delete_cart/<int:id>', delete_cartItem, name='delete_cart'),
    path('quantityIncre/<int:id>/', cartItem_quantity_incre, name='quantity_incre'),
    path('quantityDecre/<int:id>/', cartItem_quantity_decre, name='quantity_decre'),
    path('quantity_update/<int:id>/', cartItem_quantity_update, name='quantity_update'),



]
