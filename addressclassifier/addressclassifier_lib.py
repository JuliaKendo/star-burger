
from django.conf import settings
from more_itertools import first

from .models import CoordinatesAddresses
from restaurateur.geo import fetch_coordinates


def save_address(address):
    lng, lat = fetch_coordinates(
        settings.YANDEX_API_KEY, address
    )
    if lng and lat:
        CoordinatesAddresses.objects.update_or_create(
            address=address,
            defaults={
                'address': address,
                'lng': lng, 'lat': lat
            }
        )


def get_address_coordinates(address, locations):
    found_coordinates = first(
        filter(lambda location: location['address'] == address, locations)
    )
    if found_coordinates:
        return found_coordinates['lng'], found_coordinates['lat']
    return 0, 0
