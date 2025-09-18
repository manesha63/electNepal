from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from django.utils.translation import get_language
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import Candidate, CandidateEvent
from locations.models import Province, District, Municipality
import json


class CandidateListView(ListView):
    model = Candidate
    template_name = 'candidates/feed_simple_grid.html'  # Using simple 3x3 grid with row navigation
    context_object_name = 'candidates'
    paginate_by = 12

    def get_queryset(self):
        queryset = Candidate.objects.all()

        # Get filter parameters
        search = self.request.GET.get('search', '')
        district_id = self.request.GET.get('district')
        municipality_id = self.request.GET.get('municipality')
        position_level = self.request.GET.get('position')

        # Apply filters

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

        # Add current language for template
        context['current_language'] = get_language()

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
        return Candidate.objects.select_related('province', 'district', 'municipality')
    
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

    # Get current language
    current_lang = get_language()
    is_nepali = current_lang == 'ne'

    # Get candidates at different levels
    queryset = Candidate.objects.select_related('district', 'municipality', 'province')

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

        # Get location name in correct language
        if candidate.municipality:
            location = candidate.municipality.name_ne if is_nepali else candidate.municipality.name_en
        elif candidate.district:
            location = candidate.district.name_ne if is_nepali else candidate.district.name_en
        else:
            location = ""

        # Get bio, education, experience in correct language
        bio = candidate.bio_ne if is_nepali and candidate.bio_ne else candidate.bio_en
        education = candidate.education_ne if is_nepali and candidate.education_ne else candidate.education_en
        experience = candidate.experience_ne if is_nepali and candidate.experience_ne else candidate.experience_en

        candidates_data.append({
            'id': candidate.id,
            'name': candidate.full_name,
            'level': level,
            'position': candidate.get_position_level_display(),
            'location': location,
            'bio': bio if bio else '',
            'tags': [],  # Add relevant tags based on manifesto
            'photo': candidate.photo.url if candidate.photo else None,
            'likes': 0,  # Placeholder for future feature
            'supporters': 0,  # Placeholder for future feature
            'education': education if education else '',
            'experience': experience if experience else '',
            'party': 'Independent'  # All independent candidates for now
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
    
    queryset = Candidate.objects.all()
    
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
            'location': f"{candidate.municipality.name_en if candidate.municipality else ''}, {candidate.district.name_en if candidate.district else ''}"
        })
    
    return JsonResponse({'results': results})


@require_GET
def my_ballot(request):
    """
    Return candidates for the user's ballot based on their location.
    Sorted by relevance: exact ward > municipality > district > province > federal.
    """
    # Get location parameters from request
    province_id = request.GET.get('province_id')
    district_id = request.GET.get('district_id')
    municipality_id = request.GET.get('municipality_id')
    ward_number = request.GET.get('ward_number')

    # Province ID is required at minimum
    if not province_id:
        return JsonResponse({'error': 'province_id is required'}, status=400)

    try:
        province_id = int(province_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid province_id'}, status=400)

    # Build the filter query
    filters = Q(province_id=province_id) | Q(position_level='federal')

    # Convert IDs to integers if provided
    if district_id:
        try:
            district_id = int(district_id)
            filters |= Q(district_id=district_id)
        except (TypeError, ValueError):
            pass

    if municipality_id:
        try:
            municipality_id = int(municipality_id)
            filters |= Q(municipality_id=municipality_id)
        except (TypeError, ValueError):
            pass

    if ward_number:
        try:
            ward_number = int(ward_number)
            if municipality_id:
                filters |= Q(municipality_id=municipality_id, ward_number=ward_number)
        except (TypeError, ValueError):
            pass

    # Query candidates with the filters
    queryset = Candidate.objects.filter(filters)

    # Create relevance ranking based on location match
    ranking_conditions = []

    # Exact ward match (highest priority - 0)
    if municipality_id and ward_number:
        ranking_conditions.append(
            When(municipality_id=municipality_id, ward_number=ward_number, then=Value(0))
        )

    # Municipality match (priority - 1)
    if municipality_id:
        ranking_conditions.append(
            When(municipality_id=municipality_id, then=Value(1))
        )

    # District match (priority - 2)
    if district_id:
        ranking_conditions.append(
            When(district_id=district_id, then=Value(2))
        )

    # Province match (priority - 3)
    ranking_conditions.append(
        When(province_id=province_id, then=Value(3))
    )

    # Federal level (priority - 4)
    ranking_conditions.append(
        When(position_level='federal', then=Value(4))
    )

    # Apply ranking
    if ranking_conditions:
        queryset = queryset.annotate(
            relevance=Case(
                *ranking_conditions,
                default=Value(9),
                output_field=IntegerField()
            )
        ).order_by('relevance', '-created_at', 'full_name')
    else:
        queryset = queryset.order_by('-created_at', 'full_name')

    # Select related for efficiency
    queryset = queryset.select_related('province', 'district', 'municipality')

    # Get language preference
    lang = get_language()
    is_nepali = lang == 'ne'

    # Build response data
    candidates_data = []
    for candidate in queryset[:50]:  # Limit to 50 candidates for now
        # Use language-aware fields
        bio_field = 'bio_ne' if is_nepali and candidate.bio_ne else 'bio_en'
        bio_text = getattr(candidate, bio_field, '')

        # Get location display
        location_parts = []
        if candidate.ward_number:
            location_parts.append(f"Ward {candidate.ward_number}")
        if candidate.municipality:
            municipality_name = candidate.municipality.name_ne if is_nepali else candidate.municipality.name_en
            location_parts.append(municipality_name)
        if candidate.district:
            district_name = candidate.district.name_ne if is_nepali else candidate.district.name_en
            location_parts.append(district_name)
        if candidate.province:
            province_name = candidate.province.name_ne if is_nepali else candidate.province.name_en
            location_parts.append(province_name)

        location_display = ', '.join(location_parts) if location_parts else ''

        candidates_data.append({
            'id': candidate.id,
            'full_name': candidate.full_name,
            'position_level': candidate.position_level,
            'position_display': candidate.get_position_level_display(),
            'province_id': candidate.province_id,
            'district_id': candidate.district_id,
            'municipality_id': candidate.municipality_id,
            'ward_number': candidate.ward_number,
            'location': location_display,
            'bio': bio_text[:200] + '...' if len(bio_text) > 200 else bio_text,
            'photo': candidate.photo.url if candidate.photo else None,
            'party': 'Independent' if not is_nepali else 'स्वतन्त्र'
        })

    return JsonResponse({
        'candidates': candidates_data,
        'total': len(candidates_data),
        'location_context': {
            'province_id': province_id,
            'district_id': district_id,
            'municipality_id': municipality_id,
            'ward_number': ward_number
        }
    })


def ballot_view(request):
    """Display the ballot page with geolocation-based candidate sorting."""
    provinces = Province.objects.all().order_by('name_en')
    return render(request, 'candidates/ballot.html', {'provinces': provinces})


@require_GET
def candidate_cards_api(request):
    """API endpoint for candidate cards with pagination."""
    # Get parameters
    q = (request.GET.get('q') or '').strip()
    page = int(request.GET.get('page', 1))
    # "batch" = 3 rows * variable columns; front-end sends page_size
    page_size = max(1, min(int(request.GET.get('page_size', 9)), 48))

    # Build queryset
    qs = Candidate.objects.select_related('province', 'district', 'municipality')

    # Apply search filter if provided
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(bio_en__icontains=q) |
            Q(bio_ne__icontains=q)
        )

    # Order by creation date and name
    qs = qs.order_by('-created_at', 'full_name')

    # Paginate
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    def candidate_to_dict(c):
        """Convert candidate to dictionary for JSON response."""
        return {
            "id": c.id,
            "name": c.full_name,
            "photo": c.photo.url if c.photo else "/static/images/default-avatar.png",
            "position_level": c.position_level,
            "province": c.province.name_en if c.province else None,
            "district": c.district.name_en if c.district else None,
            "municipality": c.municipality.name_en if c.municipality else None,
            "ward": c.ward_number,
            "detail_url": f"/candidates/{c.id}/",
        }

    return JsonResponse({
        "items": [candidate_to_dict(c) for c in page_obj.object_list],
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "total": paginator.count,
    })