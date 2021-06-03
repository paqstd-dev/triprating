# Core
from django.shortcuts import render
from django.views import View
from django.core.cache import cache

# Project
from trips.handler import TripFinder


# Caching for 60 seconds
class SearchView(View):
    def get(self, request):
        params = request.GET
        trips = []

        if params.get('city'):
            try:
                cache_prefix = f'find_trip__trips_{ params.get("city") }_{ params.get("days") }_{ params.get("miles") }'

                if not cache.ttl(cache_prefix):
                    trips = TripFinder(
                            city=params.get('city'),
                            days=params.get('days', 7),
                            miles=params.get('miles', 400)
                        ).search()

                    cache.set(cache_prefix, trips, timeout=60)
                else:
                    trips = cache.get(cache_prefix)
            except: pass

        return render(request, 'trips/search.html', {
            'trips': trips if not params.get('show') else trips[:int(params.get('show'))] if trips else []
        })
