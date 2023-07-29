# Generated by Django 4.2.2 on 2023-07-27 20:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_alter_variant_offer_price'),
        ('offers', '0005_alter_offers_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offers',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='products.category'),
        ),
    ]
