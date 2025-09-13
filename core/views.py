from django.views.generic import TemplateView
from django.db.models import Count


class HomeView(TemplateView):
    template_name = 'core/home.html'


class AboutView(TemplateView):
    template_name = 'core/about.html'


class HowToVoteView(TemplateView):
    template_name = 'core/how_to_vote.html'
