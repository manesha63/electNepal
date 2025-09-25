from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from candidates import views as candidate_views
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/', include('locations.urls', namespace='locations_api')),

    # Language switching
    path('set-language/', core_views.set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('', candidate_views.CandidateListView.as_view(), name='home'),  # Candidates list as home
    path('about/', core_views.HomeView.as_view(), name='about'),  # About page (old home)
    path('how-to-vote/', core_views.HowToVoteView.as_view(), name='how_to_vote'),  # How to Vote page
    path('auth/', include('authentication.urls')),  # Authentication URLs with i18n support
    path('candidates/', include('candidates.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),  # JavaScript translations
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
