from django.views.generic import ListView, DetailView
from .models import Candidate

class CandidateListView(ListView):
    model = Candidate
    template_name = 'candidates/list.html'
    context_object_name = 'candidates'
    
    def get_queryset(self):
        return Candidate.objects.filter(verification_status='verified').select_related('province','district','municipality').order_by('full_name')

class CandidateDetailView(DetailView):
    model = Candidate
    template_name = 'candidates/detail.html'
    context_object_name = 'candidate'
    
    def get_queryset(self):
        return Candidate.objects.filter(verification_status='verified').select_related('province','district','municipality')
