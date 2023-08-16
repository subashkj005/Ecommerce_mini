import profile

from django.urls import path
from .views import *
from cart.views import *
from wishlist.views import *
from offers.views import *
from reviews.views import *


urlpatterns = [
    # Homepage
    path('', homepage, name='user_home'),

    # Product List
    path('product<int:id>', productpage, name='product_page'),
    path('product_list/product<int:id>/', productpage, name='product_detail'),
    path('category_page<int:id>/',category_page,name='category_page'),
    path('product_list/', product_list, name='product_list'),
    path('product_list/filter-products', filter_products, name='filter_products'),
    path('search_products', search_products, name='search_products'),

    # Cart
    path('cart', cart_page, name='cart_page'),
    path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
    # path('add_to_cart_sub<int:id>/', add_to_cart_sub, name="add_to_cart_sub"),
    path('delete_cart/<int:id>', delete_cartItem, name='delete_cart'),
    path('quantity_update/<int:id>/', cartItem_quantity_update, name='quantity_update'),
    path('checkout/',checkout, name='checkout'),

    # User Profile
    path('address', address, name='address'),
    path('profile', profile, name='profile'),
    path('account_details', account_details, name='account_details'),
    path('add_address/', add_address, name='add_address'),
    path('set_default_address<int:id>', set_default_address, name='set_default_address'),
    path('edit_address<int:id>', edit_address, name='edit_address'),
    path('del_address<int:id>/', delete_address, name='delete_address'),
    path('edit_profile/', edit_profile, name='edit_profile'),

    # Orders
    path('orders', profile_orders, name='profile_orders'),
    path('order_confirm', order_confirm, name='order_confirm'),
    path('cancel_order<int:id>/', cancel_order, name='cancel_order'),
    path('return_request<int:id>/', return_request, name='return_request'),
    path('prdouct_order_status<int:id>', prdouct_order_status, name='prdouct_order_status'),
    path('generate_pdf_invoice', generate_pdf_invoice, name='generate_pdf_invoice'),

    # Wishlist
    path('wishlist', wishlist, name='wishlist'),
    path('add_to_wishlist/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
    path('delete_wishlist_item<int:id>/', delete_wishlist_item, name='delete_wishlist_item'),
    path('wishlist_to_cart<int:id>', wishlist_to_cart, name='wishlist_to_cart'),

    # Coupons
    path('apply_coupon', apply_coupon, name='apply_coupon'),
    path('delete_cart_coupon', delete_cart_coupon, name='delete_cart_coupon'),
    
    # Reviews
    path('add_review<int:id>', add_review, name='add_review'),

    # Test case
    path('test', test_page, name='test_page'),



]
