from django.urls import path, include
from .views import *
from products.views import *
from offers.views import *



urlpatterns = [
    path('', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('home/', admin_home, name='home'),
    # Users
    path('users/', users, name="users"),
    path('user_status<int:id>', user_status, name="user_status"),
    # Category
    path('category/', categories, name="categories"),
    path('add_category/', add_category, name="add_category"),
    path('edit<int:category_id>/', edit_category, name='edit_category'),
    path('categories_delete/<int:id>/', delete_category, name='delete_category'),
    # Products
    path('products/', product_page, name='product'),
    path('edit_products<int:id>/', edit_products, name='edit_product'),
    path('delete_product<int:id>/', delete_product, name='delete_product'),
    path('delete_image<int:id>/', delete_image, name='delete_image'),
    path('add_products/', add_products, name='add_product'),
    # Variant
    path('variant/', variant_page, name='variant_page'),
    path('add_variant_page', add_variant_page, name='add_variant_page'),
    path('add_colour', add_color, name='add_colour'),
    path('add_variant', add_variant, name='add_variant'),
    path('edit_variant<int:id>/', edit_variant, name='edit_variant'),
    path('variant_delete<int:id>',variant_delete, name='variant_delete'),
    # Orders
    path('orders', orders, name='orders'),
    path('order_details<int:id>/', order_details, name='order_details'),
    path('order_status<int:ord_id>/<int:item_id>', order_status_update, name='order_status_update'),
    # Offers
    path('create_offers', create_offers, name='create_offers'),
    path('offers', offers, name='offers'),
    path('update_offers<int:id>', update_offers, name='update_offers'),
    path('offer_active<int:id>', offer_active, name='offer_active'),
    # Report
    path('filter_reports', filter_reports, name='filter_reports'),
    path('reports', reports, name='reports'),


]
