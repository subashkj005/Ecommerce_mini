import profile

from django.urls import path
from .views import *
from cart.views import *


urlpatterns = [
    path('', homepage, name='user_home'),
    path('product<int:id>', productpage, name='product_page'),
    path('category_page<int:id>/',category_page,name='category_page'),
    path('product_list/', product_list, name='product_list'),
    path('product_list/filter-products', filter_products, name='filter_products'),
    path('search_products', search_products, name='search_products'),
    path('test', test_page, name='test_page'),
    path('cart', cart_page, name='cart_page'),
    path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
    path('delete_cart/<int:id>', delete_cartItem, name='delete_cart'),
    path('quantity_update/<int:id>/', cartItem_quantity_update, name='quantity_update'),
    path('add_address/',add_address, name='add_address'),
    path('del_address<int:id>/',delete_address, name='delete_address'),
    path('edit_profile/',edit_profile, name='edit_profile'),
    path('checkout/',checkout, name='checkout'),
    path('address',address, name='address'),
    path('profile',profile, name='profile'),
    path('account_details',account_details, name='account_details'),
    path('orders',profile_orders, name='profile_orders'),
    path('order_confirm',order_confirm, name='order_confirm'),
    path('cancel_order<int:id>/', cancel_order, name='cancel_order'),
    path('return_request<int:id>/', return_request, name='return_request'),



]
