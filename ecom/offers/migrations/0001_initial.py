# Generated by Django 4.2.2 on 2023-07-27 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=3)),
                ('is_active', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='offer_images/')),
            ],
        ),
    ]