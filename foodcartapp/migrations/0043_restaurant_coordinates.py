# Generated by Django 3.2 on 2021-11-28 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0001_initial'),
        ('foodcartapp', '0042_auto_20211128_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='coordinates',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='places.place', verbose_name='адрес и координаты'),
        ),
    ]
