from django.urls import path, include

from accounts.views import *
from ecom.urls import *


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('otp/', otp, name='otp'),
    path('login/', user_login, name='user_login'),
    path('logout/', logout, name='logout'),
    path('forgot_password/', forgot_password, name='forgot'),
    path('forgot_otp/', forgot_otp, name='forgot_otp'),
    path('pass-update/', password_update, name="pass_update"),

]