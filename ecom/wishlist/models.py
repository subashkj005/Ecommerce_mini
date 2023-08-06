from django.db import models
from products.models import *
from accounts.models import *

class Wishlist(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
