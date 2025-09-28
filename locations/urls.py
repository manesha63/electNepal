from django.urls import path
from . import views

app_name = 'locations_api'

urlpatterns = [
    path('districts/', views.DistrictsByProvinceView.as_view(), name='districts_by_province'),
    path('municipalities/', views.MunicipalitiesByDistrictView.as_view(), name='municipalities_by_district'),
    path('georesolve/', views.geo_resolve, name='geo_resolve'),
    path('geo-analytics/', views.geo_analytics_stats, name='geo_analytics_stats'),
]