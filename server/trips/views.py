# Core
from django.shortcuts import render
from django.views import View
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Project
from trips.handler import TripFinder


# Caching for 60 seconds
@method_decorator(cache_page(60), name='dispatch')
class SearchView(View):
    def get(self, request):
        params = request.GET
        trips = []

        if params.get('city'):
            try:
                trips = TripFinder(
                    city=params.get('city'),
                    days=params.get('days', 7),
                    miles=params.get('miles', 400)
                ).search()
            except: pass

        return render(request, 'trips/search.html', {
            'trips': trips[:10]
        })
