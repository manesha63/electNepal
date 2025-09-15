from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Candidate, CandidateEvent
from locations.models import Province, District, Municipality
import json


class CandidateListView(ListView):
    model = Candidate
    template_name = 'candidates/feed.html'  # Using Instagram-style feed template
    context_object_name = 'candidates'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Candidate.objects.all()
        
        # Get filter parameters
        verified_only = self.request.GET.get('verified', 'true') == 'true'
        search = self.request.GET.get('search', '')
        district_id = self.request.GET.get('district')
        municipality_id = self.request.GET.get('municipality')
        position_level = self.request.GET.get('position')
        
        # Apply filters
        if verified_only:
            queryset = queryset.filter(verification_status='verified')
        
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(bio_en__icontains=search) |
                Q(bio_ne__icontains=search)
            )
        
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        if municipality_id:
            queryset = queryset.filter(municipality_id=municipality_id)
        
        if position_level:
            queryset = queryset.filter(position_level=position_level)
        
        return queryset.select_related('district', 'municipality', 'province').order_by('full_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add upcoming events
        context['upcoming_events'] = CandidateEvent.objects.filter(
            event_date__gte=timezone.now()
        ).select_related('candidate').order_by('event_date')[:5]
        
        # Add location data if available
        if self.request.GET.get('district'):
            try:
                district = District.objects.get(id=self.request.GET.get('district'))
                context['current_location'] = district
            except District.DoesNotExist:
                pass
        
        # Add provinces for location selector
        context['provinces'] = Province.objects.all()
        
        return context


class CandidateDetailView(DetailView):
    model = Candidate
    template_name = 'candidates/detail.html'
    context_object_name = 'candidate'
    
    def get_queryset(self):
        return Candidate.objects.filter(
            verification_status='verified'
        ).select_related('province', 'district', 'municipality')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add candidate's upcoming events
        context['candidate_events'] = CandidateEvent.objects.filter(
            candidate=self.object,
            event_date__gte=timezone.now()
        ).order_by('event_date')[:3]
        return context


# API endpoint for nearby candidates
def nearby_candidates_api(request):
    """API endpoint to get candidates based on location - Instagram feed style"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    # Get candidates at different levels
    queryset = Candidate.objects.filter(
        verification_status='verified'
    ).select_related('district', 'municipality', 'province')
    
    # If location provided, prioritize local candidates
    if lat and lng:
        # In production, use geocoding to get actual location
        # For now, simulate location-based filtering
        queryset = queryset.order_by('position_level', '-created_at')
    else:
        # Mix candidates from all levels
        queryset = queryset.order_by('-created_at')
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    candidates = queryset[start:end]
    has_more = queryset.count() > end
    
    candidates_data = []
    for candidate in candidates:
        # Determine level based on position
        level = 'local'
        if candidate.position_level in ['provincial']:
            level = 'provincial'
        elif candidate.position_level in ['federal']:
            level = 'federal'
        
        candidates_data.append({
            'id': candidate.id,
            'name': candidate.full_name,
            'verified': candidate.verification_status == 'verified',
            'level': level,
            'position': candidate.get_position_level_display(),
            'location': f"{candidate.municipality.name_en if candidate.municipality else candidate.district.name_en}",
            'bio': candidate.bio_en if candidate.bio_en else '',
            'tags': [],  # Add relevant tags based on manifesto
            'photo': candidate.photo.url if candidate.photo else None,
            'likes': 0,  # Placeholder for future feature
            'supporters': 0,  # Placeholder for future feature
            'education': candidate.education_en,
            'experience': candidate.experience_en
        })
    
    # Location data
    location_data = None
    if lat and lng:
        location_data = {
            'municipality': 'Kathmandu',
            'district': 'Kathmandu',
            'province': 'Bagmati Province'
        }
    
    return JsonResponse({
        'location': location_data,
        'candidates': candidates_data,
        'has_more': has_more,
        'page': page
    })


# API endpoint for searching candidates
def search_candidates_api(request):
    """API endpoint for searching candidates"""
    search_term = request.GET.get('q', '')
    district_id = request.GET.get('district')
    municipality_id = request.GET.get('municipality')
    
    queryset = Candidate.objects.filter(verification_status='verified')
    
    if search_term:
        queryset = queryset.filter(
            Q(full_name__icontains=search_term) |
            Q(bio_en__icontains=search_term) |
            Q(bio_ne__icontains=search_term)
        )
    
    if district_id:
        queryset = queryset.filter(district_id=district_id)
    
    if municipality_id:
        queryset = queryset.filter(municipality_id=municipality_id)
    
    candidates = queryset.select_related('district', 'municipality')[:20]
    
    results = []
    for candidate in candidates:
        results.append({
            'id': candidate.id,
            'name': candidate.full_name,
            'position': candidate.get_position_level_display(),
            'location': f"{candidate.municipality.name_en if candidate.municipality else ''}, {candidate.district.name_en if candidate.district else ''}",
            'verified': candidate.verification_status == 'verified'
        })
    
    return JsonResponse({'results': results})