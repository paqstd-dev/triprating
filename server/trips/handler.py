# System
import os
import csv

# Core
from django.conf import settings
from django.core.cache import cache


class TripFinder:
    _distance   :dict = {}
    _cities     :dict = {}
    _trips      :list = []
    _routes     :list = []


    def __init__(self, city:str = None, days:int = 7, miles:int = 400, cache_timeout:int = 60 * 24) -> None:
        if not city:
            return print('City is required!')
        
        # cache settings
        self._cache_timeout = cache_timeout

        self.load_distance()
        self.load_cities()

        self._city         = self.find_city(city)
        self._days         = int(days)
        self._max_miles    = int(miles)
        self._routes.append([self._city])


    # Find from cities by small city name
    # If already full path return this
    def find_city(self, current: str, population: bool = False):
        for city in self._cities:
            if current in city:
                return city if not population else self._cities[city]

        return False


    # Saving from file to list with scheme:
    def load_distance(self, filename:str = 'miles.csv') -> None:
        cache_prefix = 'find_trip__distance'

        if cache.ttl(cache_prefix):
            self._distance = cache.get(cache_prefix)
            return

        with open(settings.BASE_DIR / 'data' / filename, newline='\n') as data:  
            reader = csv.reader(data)
            header = next(reader)[1:]

            for row in reader:
                # save current city for iteration
                current = row[0]

                # Saving Y
                for index, col in enumerate(row[1:]):
                    if col == '': continue

                    if not self._distance.get(current):
                        self._distance[current] = []

                    self._distance[current].append({
                        'to': header[index],
                        'distance': float(col.replace(',', '.'))
                    })

                # Saving X
                for index, col in enumerate(row[1:]):
                    if col == '': continue

                    if not self._distance.get(header[index]):
                        self._distance[header[index]] = []

                    self._distance[header[index]].append({
                        'to': current,
                        'distance': float(col.replace(',', '.'))
                    })

            cache.set(cache_prefix, self._distance, timeout=self._cache_timeout)


    # Saving from file to list with scheme:
    def load_cities(self, filename:str = 'cities.csv') -> None:
        cache_prefix = 'find_trip__cities'

        if cache.ttl(cache_prefix):
            self._cities = cache.get(cache_prefix)
            return

        with open(settings.BASE_DIR / 'data' / filename, newline='\n') as data:  
            reader = csv.reader(data)

            # Skip headers
            next(reader, None)

            for location, population in reader:
                self._cities[location] = int(population)

            cache.set(cache_prefix, self._cities, timeout=self._cache_timeout)


    # Search next city for miles and current
    def next_city(self, current: str) -> list:
        result = [city.get('to') for city in self._distance.get(current) if city.get('distance') <= self._max_miles]
        return result


    # Core for search trips
    def search(self, rating: bool = True) -> list or None:
        while len(self._routes):
            # remove item from list and then insert if needed it
            trip = self._routes.pop(0)

            # skip if already last day
            if len(trip) > self._days: continue

            # for every city in current city to... check miles and trip
            for city in self.next_city(trip[-1]):
                current = trip + [city]

                # save trip if founded it
                if city == self._city:
                    if current not in self._trips:
                        self._trips.append(current)

                    break

                self._routes.append(current)

        if rating: return self.rating()


    # Sort and change _trips value
    def rating(self, sort: bool = True) -> list:
        trips = []

        for trip in self._trips:
            rating = 0
            routes = []

            for city in trip:
                population = self.find_city(current=city, population=True)

                routes.append({
                    'name': city,
                    'population': population
                })

                if trip.count(city) == 1:
                    rating += population

            trips.append({
                'routes': routes,
                'rating': rating
            })

        if not sort:
            return trips

        trips.sort(key=lambda item: item['rating'])
        trips.reverse()

        return trips

