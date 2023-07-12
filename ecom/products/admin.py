from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Color)
admin.site.register(Variant)
admin.site.register(ProductImage)
