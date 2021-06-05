# Core
from django.contrib import admin

# Project
from trips.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'population')

