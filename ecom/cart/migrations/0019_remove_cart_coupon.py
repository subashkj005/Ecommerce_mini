# Generated by Django 4.2.2 on 2023-08-12 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0018_cart_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='coupon',
        ),
    ]
