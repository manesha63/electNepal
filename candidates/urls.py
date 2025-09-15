from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('', views.CandidateListView.as_view(), name='list'),
    path('feed/', views.CandidateListView.as_view(), name='feed'),  # Using same view for feed
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='detail'),
]