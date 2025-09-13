from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('how-to-vote/', views.HowToVoteView.as_view(), name='how_to_vote'),
]