from django.contrib import admin

from django.contrib.gis.admin import OSMGeoAdmin
from .models import Card, Keyword

@admin.register(Card)
class CardAdmin(OSMGeoAdmin):
    list_display = ('name', 'location')

@admin.register(Keyword)
class CardAdmin(OSMGeoAdmin):
    list_display = ('name', )