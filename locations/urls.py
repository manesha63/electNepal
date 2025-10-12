from django.urls import path
from . import views
from . import api_views

app_name = 'locations_api'

urlpatterns = [
    # System endpoints
    path('health/', api_views.health_check, name='health_check'),
    path('version/', api_views.health_check, name='version'),  # Alias for health check

    # Location API endpoints
    path('districts/', api_views.districts_by_province, name='districts_by_province'),
    path('municipalities/', api_views.municipalities_by_district, name='municipalities_by_district'),
    path('municipalities/<int:municipality_id>/wards/', api_views.municipality_wards, name='municipality_wards'),
    path('georesolve/', api_views.geo_resolve, name='geo_resolve'),
    path('statistics/', api_views.location_statistics, name='location_statistics'),
]