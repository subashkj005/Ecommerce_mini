# Generated by Django 4.2.2 on 2023-08-12 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0014_alter_coupons_valid_to'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coupons',
            options={'verbose_name_plural': 'Coupons'},
        ),
        migrations.AlterModelOptions(
            name='usedcoupons',
            options={'verbose_name_plural': 'Used Coupons'},
        ),
    ]
