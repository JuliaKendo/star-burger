# Generated by Django 3.0.7 on 2021-05-10 08:20

from django.db import migrations
from django.conf import settings
from restaurateur.geo import fetch_coordinates


def fill_coordinates(apps, shema_editor):
    addresses = []
    CoordinatesAddresses = apps.get_model('foodcartapp', 'CoordinatesAddresses')
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')
    Order = apps.get_model('foodcartapp', 'Order')
    addresses.extend(Restaurant.objects.values_list('address', flat=True))
    addresses.extend(Order.objects.values_list('address', flat=True))
    for address in addresses:
        lng, lat = fetch_coordinates(settings.YANDEX_API_KEY, address)
        CoordinatesAddresses.objects.get_or_create(
            address=address,
            lng=lng, lat=lat
        )


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_auto_20210510_1059'),
    ]

    operations = [
        migrations.RunPython(fill_coordinates),
    ]
