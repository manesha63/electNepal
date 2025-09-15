from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('', views.CandidateListView.as_view(), name='list'),
    path('feed/', views.CandidateListView.as_view(), name='feed'),  # Using same view for feed
    path('ballot/', views.ballot_view, name='ballot'),
    path('api/my-ballot/', views.my_ballot, name='my_ballot'),
    path('api/cards/', views.candidate_cards_api, name='candidate_cards_api'),
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='detail'),
]