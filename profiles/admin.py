from django.contrib import admin

from django.contrib.gis.admin import OSMGeoAdmin
from .models import Profile, Keyword, ProfileCategory, ProfileCategorySocialSite

@admin.register(Profile)
class ProfileAdmin(OSMGeoAdmin):
    list_display = ('name', 'location')

@admin.register(Keyword)
class KeywordAdmin(OSMGeoAdmin):
    list_display = ('name', )

@admin.register(ProfileCategory)
class ProfileCategoryAdmin(OSMGeoAdmin):
    list_display = ('name', )

@admin.register(ProfileCategorySocialSite)
class ProfileCategorySocialSiteAdmin(OSMGeoAdmin):
    list_display = ('name', 'profile_category',)