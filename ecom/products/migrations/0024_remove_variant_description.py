# Generated by Django 4.2.2 on 2023-07-12 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_alter_productimage_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variant',
            name='description',
        ),
    ]
