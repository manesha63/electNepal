from django.views.generic import TemplateView
from django.db.models import Count
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.translation import gettext_lazy as _


class HomeView(TemplateView):
    template_name = 'core/home.html'


class AboutView(TemplateView):
    template_name = 'core/about.html'


class HowToVoteView(TemplateView):
    template_name = 'core/how_to_vote.html'


def set_language(request):
    """
    View to handle language switching via AJAX or regular requests
    """
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    language = request.GET.get('language', 'en')

    # Validate language code
    if language not in [lang[0] for lang in settings.LANGUAGES]:
        language = settings.LANGUAGE_CODE

    # Set the language
    translation.activate(language)

    # Create response
    response = HttpResponseRedirect(next_url)

    # Set language cookie that will persist
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=settings.LANGUAGE_COOKIE_AGE if hasattr(settings, 'LANGUAGE_COOKIE_AGE') else 365 * 24 * 60 * 60,
        path=settings.LANGUAGE_COOKIE_PATH if hasattr(settings, 'LANGUAGE_COOKIE_PATH') else '/',
        domain=settings.LANGUAGE_COOKIE_DOMAIN if hasattr(settings, 'LANGUAGE_COOKIE_DOMAIN') else None,
        secure=settings.LANGUAGE_COOKIE_SECURE if hasattr(settings, 'LANGUAGE_COOKIE_SECURE') else False,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY if hasattr(settings, 'LANGUAGE_COOKIE_HTTPONLY') else True,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE if hasattr(settings, 'LANGUAGE_COOKIE_SAMESITE') else 'Lax',
    )

    return response
