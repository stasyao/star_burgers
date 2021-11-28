from django.db import models


class Place(models.Model):
    longitude = models.FloatField(verbose_name='долгота', null=True)
    latitude = models.FloatField(verbose_name='широта', null=True)
    address = models.CharField(verbose_name='адрес',
                               max_length=200,
                               unique=True)
    request_date = models.DateField(verbose_name='дата запроса к геокодеру',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'координаты места'
        verbose_name_plural = 'координаты мест'

    def __str__(self):
        return self.address
