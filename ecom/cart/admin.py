from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderDetail)