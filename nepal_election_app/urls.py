from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from candidates import views as candidate_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('locations.urls', namespace='locations_api')),
    
    # Candidate API endpoints (outside i18n for consistent URLs)
    path('api/nearby-candidates/', candidate_views.nearby_candidates_api, name='nearby_candidates_api'),
    path('api/search-candidates/', candidate_views.search_candidates_api, name='search_candidates_api'),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('candidates/', include('candidates.urls')),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
