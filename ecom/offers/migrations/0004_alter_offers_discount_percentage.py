# Generated by Django 4.2.2 on 2023-07-27 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offers',
            name='discount_percentage',
            field=models.IntegerField(max_length=2),
        ),
    ]