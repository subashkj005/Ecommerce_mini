import os
from decimal import Decimal
from django.db import models
from django.apps import apps
from django.db.models import Count
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
    
    @property
    def product_rating_percentage(self):
        from reviews.models import Reviews
        reviews = Reviews.objects.filter(product=self.product)
        if reviews:
            ratings = 0
            count = 0
            for review in reviews:
                ratings += review.rating
                count+=5
            return (ratings/count)*100
        return 0
    
    @property
    def product_ratings_count(self):
        from reviews.models import Reviews
        review_count = Reviews.objects.filter(product=self.product).aggregate(total_count=Count('id'))['total_count']
        if review_count:
            return review_count
        return 0
            

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
        file_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
        if os.path.exists(file_path):
            os.remove(file_path)
            
class UserPurchasedProducts(models.Model):
    # Use strings in ForeignKey to avoid circular import reference error
    # Import apps from django.db for this use
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    products = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = 'User purchased products'

