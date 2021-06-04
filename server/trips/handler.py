# System
import csv
import json
from multiprocessing import Process

# Core
from django.conf import settings
from django.core.cache import cache
from django_redis import get_redis_connection


class TripFinder:
    _distance   :dict = {}
    _cities     :dict = {}


    # City is string, for example 'Washington' -- it is 
    def __init__(self, city:str, days:int = 7, miles:int = 400, ttl:int = 60 * 24, client:str = 'default') -> None:
        self._cache = {
            'ttl'               : ttl,
            'cities_prefix'     : f'trip_finder__cities',
            'distance_prefix'   : f'trip_finder_distance',
            'trips_prefix'      : f'trip_finder__trips_{ client }',
            'routes_prefix'     : f'trip_finder__routes_{ client }'
        }

        # Load data
        self.load_distance()
        self.load_cities()

        # Global vars
        self._city         = self.find_city(city)
        self._days         = int(days)
        self._max_miles    = int(miles)

        # Clear data
        redis = get_redis_connection('default')
        redis.delete(self._cache.get('trips_prefix'))
        redis.delete(self._cache.get('routes_prefix'))


    # Find from cities by small city name
    # If already full path return this
    def find_city(self, current:str, population:bool = False):
        city = None

        if current in self._cities:
            city = current
        else:
            for c in self._cities:
                if current in c:
                    city = c
                    break

        return self._cities[city] if population else city


    # Saving from file to list with scheme:
    def load_distance(self, filename:str = 'miles.csv') -> None:
        cache_prefix = self._cache.get('distance_prefix')

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

            cache.set(cache_prefix, self._distance, timeout=self._cache.get('ttl'))


    # Saving from file to list with scheme:
    def load_cities(self, filename:str = 'cities.csv') -> None:
        cache_prefix = self._cache.get('cities_prefix')

        if cache.ttl(cache_prefix):
            self._cities = cache.get(cache_prefix)
            return

        with open(settings.BASE_DIR / 'data' / filename, newline='\n') as data:  
            reader = csv.reader(data)

            # Skip headers
            next(reader, None)

            for location, population in reader:
                self._cities[location] = int(population)

            cache.set(cache_prefix, self._cities, timeout=self._cache.get('ttl'))


    # Search next city for miles and current
    def next_city(self, current: str) -> list:
        result = [city.get('to') for city in self._distance.get(current) if city.get('distance') <= self._max_miles]
        return result


    # Trying get from b'[list]' list()
    # Redis by default return string and we must convert to python list
    def _parseList(self, string:str):
        try: return json.loads(string)
        except: return []


    # Core for search trips
    def search(self) -> None:
        redis = get_redis_connection('default')

        cr = self._cache.get('routes_prefix')
        ct  = self._cache.get('trips_prefix')

        if not redis.llen(cr):
            redis.rpush(cr, json.dumps([self._city]))

        while redis.llen(cr):
            # Remove item from list and then insert if needed it
            trip = self._parseList(redis.lpop(cr))

            # Skip if already last day
            if not trip or len(trip) > self._days: continue

            # For every city in current city to... check miles and trip
            for city in self.next_city(trip[-1]):
                current = trip + [city]

                # Save trip if founded it
                if len(current) >= self._days:
                    if city == self._city:
                        redis.rpush(ct, json.dumps(current))
                        break

                    continue

                redis.rpush(cr, json.dumps(current))

        redis.expire(self._cache.get('routes_prefix'), 60)
        redis.expire(self._cache.get('trips_prefix'), 60)


    def multisearch(self, workers:int = 16):
        procs = []

        for _ in range(workers):
            proc = Process(target=self.search)
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()


    # Sort and change _trips value
    def rating(self) -> list:
        redis = get_redis_connection('default')

        # Cached Trips (cts) and Cached Trip (ct)
        cts = redis.lrange(self._cache.get('trips_prefix'), start=0, end=-1)

        trips = []
        for ct in cts:
            trip = self._parseList(ct)

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

        trips.sort(key=lambda item: item['rating'])
        trips.reverse()

        return trips

