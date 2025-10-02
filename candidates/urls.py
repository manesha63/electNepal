from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('', views.CandidateListView.as_view(), name='list'),
    path('feed/', views.CandidateListView.as_view(), name='feed'),  # Using same view for feed
    path('ballot/', views.ballot_view, name='ballot'),

    # Registration and Dashboard
    path('register/', views.candidate_register, name='register'),
    path('dashboard/', views.CandidateDashboardView.as_view(), name='dashboard'),
    path('edit/', views.edit_profile, name='edit'),
    # Posts URLs removed - candidates can only create events
    # path('posts/add/', views.add_post, name='add_post'),
    # path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('registration-success/', views.registration_success, name='registration_success'),

    # APIs
    path('api/my-ballot/', views.my_ballot, name='my_ballot'),
    path('api/cards/', views.candidate_cards_api, name='candidate_cards_api'),

    # Detail view (keep at the end to avoid conflicts)
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='detail'),
]