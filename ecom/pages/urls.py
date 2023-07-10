from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='user_home'),
    path('product<int:id>', productpage, name='product_page'),
    path('test', test_page, name='test_page'),
    path('profile', profile_page, name='profile_page'),



]
