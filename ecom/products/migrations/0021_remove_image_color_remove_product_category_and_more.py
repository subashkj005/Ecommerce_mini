# Generated by Django 4.2.2 on 2023-07-11 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_color_specificationvariant_product_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='color',
        ),
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.RemoveField(
            model_name='specificationvariant',
            name='color',
        ),
        migrations.DeleteModel(
            name='Color',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.DeleteModel(
            name='SpecificationVariant',
        ),
    ]
