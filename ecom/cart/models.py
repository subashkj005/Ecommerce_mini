from django.db import models
import random
import string
from django.contrib.auth.models import User
from products.models import Variant
from accounts.models import *




# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE,null=True, blank=True)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total = models.PositiveIntegerField(default=0)

    def calculate_total_price(self):
        return self.variant.price * self.quantity

    def __str__(self):
        return self.variant.product.name+" "+self.variant.name+" "+self.variant.colour.name



class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('order_pending', 'Order_Pending'),
        ('order_confirmed', 'Order_Confirmed'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('cash_on_delivery', 'Cash_on_Delivery'),
        ('online_payment', 'Online_payment'),
    )

    def generate_order_id():
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(10))

    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now=True)
    order_num = models.CharField(max_length=20, default=generate_order_id)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default='order_pending')
    payment_type = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default="Cash on delivery")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class OrderDetail(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10,decimal_places=2, default=0)

