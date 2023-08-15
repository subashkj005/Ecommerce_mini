from django.db import models
from products.models import *
from accounts.models import Profile

class Reviews(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    review = models.TextField(max_length=200)
    rating = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Reviews'