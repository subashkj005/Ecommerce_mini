import os
from decimal import Decimal
from django.db import models
from django.apps import AppConfig
from django.db.models.signals import pre_delete, pre_save
from django.utils import timezone
from django.dispatch import receiver
from django.conf import settings




# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='categories_images')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Color(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    colour = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='variant_colours')
    name = models.CharField(max_length=50)
    stock = models.IntegerField()
    price = models.FloatField()
    original_price = models.DecimalField(max_digits=10,decimal_places=2,default=0, null=True, blank=True)
    discount = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def calculate_discount_price(self, offer_rate):
        variant_price = Decimal(str(self.price))
        return variant_price * offer_rate/100

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='colour_images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image of {self.product.name} {self.color.name}"

@receiver(pre_delete, sender=ProductImage)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        print('-----Instance Found------')
        file_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
        if os.path.exists(file_path):
            print('------File Removed------')
            os.remove(file_path)

