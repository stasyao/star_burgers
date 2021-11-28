from django.contrib import admin

from places.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['address', 'latitude', 'longitude', 'request_date', ]
