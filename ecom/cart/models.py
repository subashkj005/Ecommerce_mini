from django.db import models
import random
import string
from django.db.models import Sum
from products.models import Variant
from accounts.models import *
from offers.models import Coupons




# Create your models here.


class Cart(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE,null=True, blank=True)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variants')
    quantity = models.PositiveIntegerField(default=1)
    total = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def calculate_discount(self):
        return self.variant.original_price - self.variant.price

    def calculate_total_price(self):
        return self.variant.price * self.quantity

    def calculate_total_quantity_discount(self):
        return self.quantity * self.variant.discount


    def total_discount_in_cart(self, user):
        total_discount = Cart.objects.filter(user=user).aggregate(total=Sum('variant__discount'))['total']
        return total_discount if total_discount else 0

    def __str__(self):
        return self.variant.product.name+"---"+self.variant.name+"---"+self.variant.colour.name



class Order(models.Model):
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
    payment_type = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default="Cash on delivery")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.name+"---"+self.order_num



class OrderDetail(models.Model):

    ORDER_STATUS_CHOICES = (
        ('order_pending', 'Order_Pending'),
        ('order_confirmed', 'Order_Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default='order_pending')
    is_returned = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivered_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.order.user.name+"---"+self.product.product.name+"---"+self.order_status

