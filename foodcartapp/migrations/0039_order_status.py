# Generated by Django 3.2 on 2021-11-28 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_auto_20211128_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'обработан'), (2, 'не обработан')], db_index=True, default=2, verbose_name='статус заказа'),
        ),
    ]
