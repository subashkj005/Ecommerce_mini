from django.urls import path, include
from .views import *
from products.views import *



urlpatterns = [
    path('', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('home/', admin_home, name='home'),
    path('users/', users, name="users"),
    path('user_status<int:id>', user_status, name="user_status"),
    path('category/', categories, name="categories"),
    path('add_category/', add_category, name="add_category"),
    path('edit<int:category_id>/', edit_category, name='edit_category'),
    path('categories_delete/<int:id>/', delete_category, name='delete_category'),
    path('products/', product_page, name='product'),
    path('edit_products<int:id>/', edit_products, name='edit_product'),
    path('delete_product<int:id>/', delete_product, name='delete_product'),
    path('add_products/', add_products, name='add_product'),


]
