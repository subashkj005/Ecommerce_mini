# Generated by Django 4.2.2 on 2023-07-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0011_remove_cart_offer_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='discount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
