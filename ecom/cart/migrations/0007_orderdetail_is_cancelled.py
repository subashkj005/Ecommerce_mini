# Generated by Django 4.2.2 on 2023-07-25 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_remove_order_order_status_orderdetail_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='is_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]