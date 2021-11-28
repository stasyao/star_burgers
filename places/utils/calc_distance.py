import requests

from geopy import distance

from places.models import Place
from star_burger.settings import GECOCODER_API_KEY


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": GECOCODER_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coordinates_from_db_or_create(queryset, address):
    for place in queryset:
        if place.address == address:
            return place.longitude, place.latitude
    else:
        lon, lat = fetch_coordinates(address)
        queryset.append(Place.objects.create(longitude=lon,
                                             latitude=lat,
                                             address=address))
        return lon, lat


def calc_distance(queryset, address1, address2):
    return round(
        distance.distance(
            get_coordinates_from_db_or_create(queryset, address1),
            get_coordinates_from_db_or_create(queryset, address2)
        ).km, 2
    )
