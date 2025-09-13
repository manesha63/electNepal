from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('', views.CandidateListView.as_view(), name='list'),
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='detail'),
]