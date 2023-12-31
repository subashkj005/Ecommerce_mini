# Generated by Django 4.2.2 on 2023-08-08 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0014_alter_coupons_valid_to'),
        ('cart', '0017_orderdetail_delivered_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='coupon',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='offers.coupons'),
        ),
    ]
