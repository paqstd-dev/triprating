# System
import csv

# Core
from django.core.management.base import BaseCommand
from django.conf import settings

# Project
from trips.models import City, Distance


class Command(BaseCommand):
    help = 'Load files to db'


    def handle(self, *args, **options):
        # open and save cities data
        with open(settings.BASE_DIR / 'data/cities.csv', newline='\n') as data:
            cities = {}

            reader = csv.reader(data)

            # Skip headers
            next(reader, None)

            for location, population in reader:
                cities[location] = int(population)

            # clear data
            City.objects.all().delete()

            # insert data
            City.objects.bulk_create([City(name=name, population=population) for name, population in cities.items()])

