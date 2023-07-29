# Generated by Django 4.2.2 on 2023-07-27 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_variant_offer_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='offer_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
