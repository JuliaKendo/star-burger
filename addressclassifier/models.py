from django.db import models
from django.utils import timezone


class CoordinatesAddressesQuerySet(models.QuerySet):

    def get_coordinates(self, addresses):
        return self.filter(
            address__in=addresses
        )


class CoordinatesAddresses(models.Model):
    updated_at = models.DateTimeField(
        'Дата обновления', default=timezone.now, db_index=True
    )
    address = models.CharField('адрес', max_length=100, unique=True)
    lng = models.FloatField(verbose_name='Долгота')
    lat = models.FloatField(verbose_name='Широта')

    objects = CoordinatesAddressesQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        verbose_name = 'Координаты адресов'
        verbose_name_plural = 'Координаты адресов'

    def __str__(self):
        return self.address
