# Generated by Django 3.2 on 2021-11-28 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_restaurant_coordinates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='coordinates',
        ),
    ]
