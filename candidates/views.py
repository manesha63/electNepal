from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from django.utils.translation import get_language, gettext as _
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from .models import Candidate, CandidateEvent, CandidatePost
from .forms import CandidateRegistrationForm, CandidateUpdateForm, CandidatePostForm, CandidateEventForm
from locations.models import Province, District, Municipality
import json
import hashlib


class CandidateListView(ListView):
    model = Candidate
    template_name = 'candidates/feed_simple_grid.html'  # Using simple 3x3 grid with row navigation
    context_object_name = 'candidates'
    paginate_by = 12

    def get_queryset(self):
        queryset = Candidate.objects.filter(status='approved')  # Only show approved candidates

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
        return Candidate.objects.filter(status='approved').select_related('province', 'district', 'municipality')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add candidate's upcoming events
        context['candidate_events'] = CandidateEvent.objects.filter(
            candidate=self.object,
            event_date__gte=timezone.now()
        ).order_by('event_date')[:3]
        return context


# API endpoint for nearby candidates
@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def nearby_candidates_api(request):
    """API endpoint to get candidates based on location - Instagram feed style"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    page = int(request.GET.get('page', 1))
    per_page = 10

    # Get current language
    current_lang = get_language()
    is_nepali = current_lang == 'ne'

    # Get candidates at different levels - only show approved
    queryset = Candidate.objects.filter(status='approved').select_related('district', 'municipality', 'province')

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
@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def search_candidates_api(request):
    """API endpoint for searching candidates"""
    search_term = request.GET.get('q', '')
    district_id = request.GET.get('district')
    municipality_id = request.GET.get('municipality')
    
    queryset = Candidate.objects.filter(status='approved')  # Only show approved candidates
    
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
@ratelimit(key='ip', rate='30/m', method='GET', block=True)  # 30 requests per minute per IP
def my_ballot(request):
    """
    Return candidates for the user's ballot based on their location.
    Sorted by relevance: exact ward > municipality > district > province > federal.
    Implements caching and pagination to reduce database load.
    """
    # Get location parameters from request
    province_id = request.GET.get('province_id')
    district_id = request.GET.get('district_id')
    municipality_id = request.GET.get('municipality_id')
    ward_number = request.GET.get('ward_number')

    # Get pagination parameters
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 20)  # Default 20 candidates per page

    try:
        page = int(page)
        page_size = min(int(page_size), 100)  # Max 100 per page for safety
    except (TypeError, ValueError):
        page = 1
        page_size = 20

    # Province ID is required at minimum
    if not province_id:
        return JsonResponse({'error': 'province_id is required'}, status=400)

    # Generate cache key based on location, language, and pagination
    lang = get_language()
    cache_key_parts = [
        'ballot',
        lang,
        str(province_id),
        str(district_id or ''),
        str(municipality_id or ''),
        str(ward_number or ''),
        str(page),
        str(page_size)
    ]
    cache_key = f"my_ballot:{':'.join(cache_key_parts)}"

    # Try to get cached result
    cached_result = cache.get(cache_key)
    if cached_result:
        return JsonResponse(cached_result)

    try:
        province_id = int(province_id)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid province_id'}, status=400)

    # Convert IDs to integers if provided
    if district_id:
        try:
            district_id = int(district_id)
        except (TypeError, ValueError):
            district_id = None

    if municipality_id:
        try:
            municipality_id = int(municipality_id)
        except (TypeError, ValueError):
            municipality_id = None

    if ward_number:
        try:
            ward_number = int(ward_number)
        except (TypeError, ValueError):
            ward_number = None

    # Build the filter query based on position levels and location hierarchy
    # Each position level should only show candidates that match the appropriate location level
    filters = Q()

    # Federal level candidates (nationwide) - always included
    # Support both old and new position values
    filters |= Q(position_level__in=['house_of_representatives', 'national_assembly', 'federal'])

    # Provincial level candidates - must be in user's province
    filters |= Q(
        position_level__in=['provincial_assembly', 'provincial'],
        province_id=province_id
    )

    # Municipal level candidates (Mayor/Deputy Mayor) - must be in user's exact municipality
    if municipality_id:
        filters |= Q(
            position_level__in=['mayor_chairperson', 'deputy_mayor_vice_chairperson', 'local_executive', 'local'],
            province_id=province_id,
            district_id=district_id,
            municipality_id=municipality_id
        )

    # Ward level candidates - must be in user's exact ward
    if municipality_id and ward_number:
        filters |= Q(
            position_level__in=['ward_chairperson', 'ward_member', 'ward'],
            province_id=province_id,
            district_id=district_id,
            municipality_id=municipality_id,
            ward_number=ward_number
        )

    # Query candidates with the filters and ensure they're approved
    queryset = Candidate.objects.filter(filters, status='approved')

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

    # Get language preference (already fetched above for cache key)
    is_nepali = lang == 'ne'

    # Paginate the queryset
    paginator = Paginator(queryset, page_size)

    try:
        page_obj = paginator.get_page(page)
    except EmptyPage:
        page_obj = paginator.get_page(1)  # Return first page if page is out of range

    # Build response data
    candidates_data = []
    ward_label = _("Ward")  # Import moved outside loop

    for candidate in page_obj.object_list:
        # Use language-aware fields
        bio_field = 'bio_ne' if is_nepali and candidate.bio_ne else 'bio_en'
        bio_text = getattr(candidate, bio_field, '')

        # Get location display
        location_parts = []
        if candidate.ward_number:
            location_parts.append(f"{ward_label} {candidate.ward_number}")
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

        # Preserve language prefix in detail URL
        lang_prefix = '/ne' if is_nepali else ''

        candidates_data.append({
            'id': candidate.id,
            'name': candidate.full_name,  # Changed to match candidate_cards_api
            'photo': candidate.photo.url if candidate.photo else settings.DEFAULT_CANDIDATE_AVATAR,
            'position_level': candidate.position_level,
            'province': province_name if candidate.province else None,
            'district': district_name if candidate.district else None,
            'municipality': municipality_name if candidate.municipality else None,
            'ward': candidate.ward_number,  # Changed to match candidate_cards_api
            'detail_url': f'{lang_prefix}/candidates/{candidate.id}/',  # Preserve language prefix
            # Additional fields for ballot page
            'province_id': candidate.province_id,
            'district_id': candidate.district_id,
            'municipality_id': candidate.municipality_id,
            'bio': bio_text[:200] + '...' if len(bio_text) > 200 else bio_text,
            'party': 'Independent' if not is_nepali else 'स्वतन्त्र'
        })

    # Prepare response data with pagination info
    response_data = {
        'candidates': candidates_data,
        'total': paginator.count,  # Total candidates across all pages
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page_size': page_size,
        'location_context': {
            'province_id': province_id,
            'district_id': district_id,
            'municipality_id': municipality_id,
            'ward_number': ward_number
        }
    }

    # Cache the result for 5 minutes (300 seconds)
    cache.set(cache_key, response_data, 300)

    return JsonResponse(response_data)


def ballot_view(request):
    """Display the ballot page with geolocation-based candidate sorting."""
    provinces = Province.objects.all().order_by('name_en')
    return render(request, 'candidates/ballot.html', {'provinces': provinces})


@require_GET
@ratelimit(key='ip', rate='60/m', method='GET', block=True)  # 60 requests per minute for general browsing
def candidate_cards_api(request):
    """API endpoint for candidate cards with pagination."""
    # Get parameters
    q = (request.GET.get('q') or '').strip()
    page = int(request.GET.get('page', 1))
    # "batch" = 3 rows * variable columns; front-end sends page_size
    page_size = max(1, min(int(request.GET.get('page_size', 9)), 48))

    # Get filter parameters
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    municipality_id = request.GET.get('municipality')
    position_level = request.GET.get('position')

    # Build queryset - only show approved candidates
    qs = Candidate.objects.filter(status='approved').select_related('province', 'district', 'municipality')

    # Apply search filter if provided - search in all relevant fields
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(bio_en__icontains=q) |
            Q(bio_ne__icontains=q) |
            Q(education_en__icontains=q) |
            Q(education_ne__icontains=q) |
            Q(experience_en__icontains=q) |
            Q(experience_ne__icontains=q) |
            Q(manifesto_en__icontains=q) |
            Q(manifesto_ne__icontains=q)
        )

    # Apply location filters
    if province_id:
        qs = qs.filter(province_id=province_id)
    if district_id:
        qs = qs.filter(district_id=district_id)
    if municipality_id:
        qs = qs.filter(municipality_id=municipality_id)
    if position_level:
        qs = qs.filter(position_level=position_level)

    # Order by creation date and name
    qs = qs.order_by('-created_at', 'full_name')

    # Paginate
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    def candidate_to_dict(c):
        """Convert candidate to dictionary for JSON response."""
        from django.utils.translation import get_language
        lang = get_language()
        is_nepali = lang == 'ne'

        # Preserve language prefix in detail URL
        lang_prefix = '/ne' if is_nepali else ''

        return {
            "id": c.id,
            "name": c.full_name,
            "photo": c.photo.url if c.photo else settings.DEFAULT_CANDIDATE_AVATAR,
            "position_level": c.position_level,
            "province": getattr(c.province, 'name_ne' if is_nepali else 'name_en', None) if c.province else None,
            "district": getattr(c.district, 'name_ne' if is_nepali else 'name_en', None) if c.district else None,
            "municipality": getattr(c.municipality, 'name_ne' if is_nepali else 'name_en', None) if c.municipality else None,
            "ward": c.ward_number,
            "detail_url": f"{lang_prefix}/candidates/{c.id}/",
        }

    return JsonResponse({
        "items": [candidate_to_dict(c) for c in page_obj.object_list],
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "total": paginator.count,
    })


# Candidate Registration and Dashboard Views
@login_required
def candidate_register(request):
    """Handle candidate registration for authenticated users."""
    # Check if user already has a candidate profile
    if hasattr(request.user, 'candidate'):
        messages.info(request, 'You already have a candidate profile.')
        return redirect('candidates:dashboard')

    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user
            candidate.status = 'pending'  # Set to pending for admin review
            candidate.save()

            # Send email notifications
            try:
                # Send confirmation to candidate
                candidate.send_registration_confirmation()
                # Notify admins about new registration
                candidate.notify_admin_new_registration()
            except Exception as e:
                # Log error but don't fail the registration
                print(f"Email notification error: {e}")

            messages.success(request, 'Your candidate profile has been submitted for review! You will be notified once approved.')
            return redirect('candidates:registration_success')
    else:
        form = CandidateRegistrationForm()

    # Get location data for dropdowns
    provinces = Province.objects.all().order_by('name_en')

    return render(request, 'candidates/register.html', {
        'form': form,
        'provinces': provinces,
    })


class CandidateDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for candidates to manage their profile."""
    template_name = 'candidates/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if user has a candidate profile
        if not hasattr(request.user, 'candidate'):
            messages.warning(request, 'You need to create a candidate profile first.')
            return redirect('candidates:register')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = self.request.user.candidate

        context['candidate'] = candidate
        context['posts'] = candidate.posts.all().order_by('-created_at')[:5]
        context['events'] = candidate.events.filter(
            event_date__gte=timezone.now()
        ).order_by('event_date')[:5]
        context['can_edit'] = candidate.status == 'approved'

        return context


@login_required
def edit_profile(request):
    """Edit candidate profile (only for approved candidates)."""
    if not hasattr(request.user, 'candidate'):
        return redirect('candidates:register')

    candidate = request.user.candidate

    # Only approved candidates can edit their profile
    if candidate.status != 'approved':
        messages.error(request, 'Your profile must be approved before you can edit it.')
        return redirect('candidates:dashboard')

    if request.method == 'POST':
        # Handle simple form data from dashboard modal
        candidate.bio_en = request.POST.get('bio_en', candidate.bio_en)
        candidate.manifesto_en = request.POST.get('manifesto_en', candidate.manifesto_en)
        candidate.experience_en = request.POST.get('experience_en', candidate.experience_en)
        candidate.education_en = request.POST.get('education_en', candidate.education_en)
        candidate.website = request.POST.get('website', candidate.website)
        candidate.facebook_url = request.POST.get('facebook_url', candidate.facebook_url)
        candidate.donation_link = request.POST.get('donation_link', candidate.donation_link)
        candidate.donation_description = request.POST.get('donation_description', candidate.donation_description)

        # Auto-translate if needed
        candidate.autotranslate_missing()
        candidate.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('candidates:dashboard')

    # If someone directly accesses /candidates/edit/ via GET, redirect to dashboard
    return redirect('candidates:dashboard')


@login_required
def add_post(request):
    """Add a new campaign post (only for approved candidates)."""
    if not hasattr(request.user, 'candidate'):
        return redirect('candidates:register')

    candidate = request.user.candidate

    if candidate.status != 'approved':
        messages.error(request, 'Your profile must be approved before you can add posts.')
        return redirect('candidates:dashboard')

    if request.method == 'POST':
        form = CandidatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.candidate = candidate
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('candidates:dashboard')
    else:
        form = CandidatePostForm()

    return render(request, 'candidates/add_post.html', {
        'form': form,
        'candidate': candidate
    })


@login_required
def add_event(request):
    """Add a new campaign event (only for approved candidates)."""
    if not hasattr(request.user, 'candidate'):
        return redirect('candidates:register')

    candidate = request.user.candidate

    if candidate.status != 'approved':
        messages.error(request, 'Your profile must be approved before you can add events.')
        return redirect('candidates:dashboard')

    if request.method == 'POST':
        form = CandidateEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.candidate = candidate
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('candidates:dashboard')
    else:
        form = CandidateEventForm()

    return render(request, 'candidates/add_event.html', {
        'form': form,
        'candidate': candidate
    })


def registration_success(request):
    """Display success page after candidate registration."""
    return render(request, 'candidates/registration_success.html')