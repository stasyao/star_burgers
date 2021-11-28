# Generated by Django 3.2 on 2021-11-28 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('longitude', models.FloatField(null=True, verbose_name='долгота')),
                ('latitude', models.FloatField(null=True, verbose_name='широта')),
                ('address', models.CharField(max_length=200, unique=True, verbose_name='адрес')),
                ('request_date', models.DateField(auto_now_add=True, verbose_name='дата запроса к геокодеру')),
            ],
            options={
                'verbose_name': 'координаты места',
                'verbose_name_plural': 'координаты мест',
            },
        ),
    ]
