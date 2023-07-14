# Generated by Django 4.2.2 on 2023-07-10 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_productimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('color_code', models.CharField(max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='productimage',
            name='image_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('stock', models.IntegerField()),
                ('price', models.FloatField()),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.color')),
            ],
        ),
        migrations.AddField(
            model_name='color',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='colors', to='products.product'),
        ),
    ]