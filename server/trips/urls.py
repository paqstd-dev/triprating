from django.urls import path
from trips.views import SearchView


urlpatterns = [
    path('', SearchView.as_view(), name='search')
]