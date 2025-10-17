"""
API Views for Candidates with proper documentation
"""

import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Case, When, Value, IntegerField, CharField, Func
from django.core.paginator import Paginator
from django.utils.translation import get_language
from django.views.decorators.vary import vary_on_headers
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import Candidate
from .serializers import (
    CandidateCardSerializer,
    CandidateBallotSerializer,
    LocationFilterSerializer,
    PaginationSerializer,
    SearchSerializer
)


def sanitize_search_input(query_string):
    """
    Sanitize user search input to prevent any potential injection attacks.

    Defense-in-depth: While Django ORM already uses parameterized queries,
    this provides an additional layer of protection by:
    1. Limiting length to prevent DoS
    2. Removing control characters
    3. Normalizing whitespace

    Args:
        query_string (str): Raw user input

    Returns:
        str: Sanitized query string safe for database queries
    """
    if not query_string:
        return ''

    # Strip leading/trailing whitespace
    sanitized = query_string.strip()

    # Limit length to prevent extremely long queries (DoS prevention)
    max_length = 200
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove control characters (except space, tab, newline which normalize to space)
    # Keep alphanumeric, spaces, and common punctuation
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', sanitized)

    # Normalize multiple whitespace to single space
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Final strip
    sanitized = sanitized.strip()

    return sanitized


@extend_schema(
    summary="Get candidate cards for feed",
    description="Returns paginated list of approved candidates for the main feed display. Supports search and filtering.",
    parameters=[
        OpenApiParameter(name='q', type=str, description='Search query for candidate name or bio'),
        OpenApiParameter(name='province', type=int, description='Filter by province ID'),
        OpenApiParameter(name='district', type=int, description='Filter by district ID'),
        OpenApiParameter(name='municipality', type=int, description='Filter by municipality ID'),
        OpenApiParameter(name='position', type=str, description='Filter by position level', enum=[
            'federal', 'provincial', 'mayor', 'deputy_mayor', 'ward',
            'ward_member', 'womens_member', 'dalit_womens_member', 'local_executive'
        ]),
        OpenApiParameter(name='page', type=int, description='Page number (default: 1)'),
        OpenApiParameter(name='page_size', type=int, description='Items per page (default: 9, max: 48)'),
    ],
    responses={
        200: OpenApiResponse(
            description="Successful response with candidate cards",
            response={
                'type': 'object',
                'properties': {
                    'results': {'type': 'array', 'items': {'$ref': '#/components/schemas/CandidateCard'}},
                    'total': {'type': 'integer', 'description': 'Total number of candidates'},
                    'page': {'type': 'integer', 'description': 'Current page number'},
                    'page_size': {'type': 'integer', 'description': 'Items per page'},
                    'total_pages': {'type': 'integer', 'description': 'Total number of pages'},
                    'has_next': {'type': 'boolean', 'description': 'Whether there is a next page'},
                    'has_previous': {'type': 'boolean', 'description': 'Whether there is a previous page'},
                }
            }
        )
    },
    tags=['Candidates']
)
@api_view(['GET'])
@vary_on_headers('Accept-Language')
@ratelimit(key='ip', rate='60/m', method='GET', block=True)  # 60 requests per minute per IP
def candidate_cards_api(request):
    """
    API endpoint for candidate cards with pagination.

    Returns a paginated list of approved candidates with their basic information
    for display in card format on the main feed.
    """
    # Get parameters
    q_raw = request.GET.get('q') or ''
    q = sanitize_search_input(q_raw)  # Sanitize search input for security
    page = int(request.GET.get('page', 1))
    page_size = max(1, min(int(request.GET.get('page_size', 9)), 48))

    # Get filter parameters
    province_id = request.GET.get('province')
    district_id = request.GET.get('district')
    municipality_id = request.GET.get('municipality')
    position_level = request.GET.get('position')

    # Build queryset - only show approved candidates
    qs = Candidate.objects.filter(status='approved').select_related('province', 'district', 'municipality')

    # Track if we're using search ranking (to preserve sort order)
    using_search_rank = False

    # Apply search filter using PostgreSQL Full-Text Search (indexed, fast)
    # Skip FTS for single character queries (PostgreSQL limitation)
    # Also escape boolean operators to treat them literally
    if q and len(q) >= 2:  # Minimum 2 characters for FTS
        # Escape boolean operators (AND, OR, NOT) by replacing them with spaces
        # This prevents PostgreSQL from interpreting them as search operators
        escaped_query = q
        # Replace boolean operators with quoted versions to treat them literally
        for operator in ['AND', 'OR', 'NOT']:
            escaped_query = re.sub(r'\b' + operator + r'\b', ' ', escaped_query, flags=re.IGNORECASE)

        # Normalize multiple spaces that may result from replacements
        escaped_query = re.sub(r'\s+', ' ', escaped_query).strip()

        # Only proceed if we still have a query after escaping
        if escaped_query:
            # Use the existing GIN index for full-text search
            # This is MUCH faster than ILIKE on large datasets
            search_vector = (
                SearchVector('full_name', weight='A') +
                SearchVector('bio_en', weight='B') +
                SearchVector('bio_ne', weight='B') +
                SearchVector('education_en', weight='C') +
                SearchVector('education_ne', weight='C') +
                SearchVector('experience_en', weight='C') +
                SearchVector('experience_ne', weight='C') +
                SearchVector('manifesto_en', weight='D') +
                SearchVector('manifesto_ne', weight='D')
            )
            search_query = SearchQuery(escaped_query)

            # Add ts_headline for search result highlighting
            # This highlights matched terms in the search results with <mark> tags
            qs = qs.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                # Highlight matches in bio_en
                bio_en_highlighted=Func(
                    Value('english'),
                    'bio_en',
                    search_query,
                    Value('StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25'),
                    function='ts_headline',
                    output_field=CharField()
                ),
                # Highlight matches in bio_ne (Nepali uses simple dictionary)
                bio_ne_highlighted=Func(
                    Value('simple'),
                    'bio_ne',
                    search_query,
                    Value('StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25'),
                    function='ts_headline',
                    output_field=CharField()
                ),
                # Highlight matches in education_en
                education_en_highlighted=Func(
                    Value('english'),
                    'education_en',
                    search_query,
                    Value('StartSel=<mark>, StopSel=</mark>, MaxWords=30, MinWords=15'),
                    function='ts_headline',
                    output_field=CharField()
                ),
                # Highlight matches in education_ne
                education_ne_highlighted=Func(
                    Value('simple'),
                    'education_ne',
                    search_query,
                    Value('StartSel=<mark>, StopSel=</mark>, MaxWords=30, MinWords=15'),
                    function='ts_headline',
                    output_field=CharField()
                )
            ).filter(search=search_query).order_by('-rank')
            using_search_rank = True  # Mark that we're using search ranking
    elif q and len(q) == 1:
        # For single character searches, use simple ILIKE on name only
        # This is less efficient but works for single characters
        qs = qs.filter(full_name__icontains=q)

    # Apply location filters
    if province_id:
        qs = qs.filter(province_id=province_id)
    if district_id:
        qs = qs.filter(district_id=district_id)
    if municipality_id:
        qs = qs.filter(municipality_id=municipality_id)
    if position_level:
        qs = qs.filter(position_level=position_level)

    # Order by creation date (newest first) - ONLY if not using search ranking
    # This preserves the search relevance order when user is searching
    if not using_search_rank:
        qs = qs.order_by('-created_at')

    # Limit total results to prevent memory issues (max 1000 results)
    # Convert to list to enforce hard limit and avoid queryset issues with Paginator
    total_count = qs.count()
    if total_count > 1000:
        qs = list(qs[:1000])

    # Paginate
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    # Serialize
    serializer = CandidateCardSerializer(page_obj.object_list, many=True, context={'request': request})

    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })


@extend_schema(
    summary="Get candidates for user's ballot",
    description="""
    Returns candidates for the user's ballot based on their location.
    Candidates are sorted by relevance: exact ward match > municipality > district > province > federal.
    This endpoint is used for the ballot feature where users see candidates relevant to their voting location.
    """,
    parameters=[
        OpenApiParameter(name='province_id', type=int, description='User\'s province ID'),
        OpenApiParameter(name='district_id', type=int, description='User\'s district ID'),
        OpenApiParameter(name='municipality_id', type=int, description='User\'s municipality ID'),
        OpenApiParameter(name='ward_number', type=int, description='User\'s ward number'),
        OpenApiParameter(name='page', type=int, description='Page number (default: 1)'),
        OpenApiParameter(name='page_size', type=int, description='Items per page (default: 20, max: 100)'),
    ],
    responses={
        200: OpenApiResponse(
            description="Successful response with ballot candidates",
            response={
                'type': 'object',
                'properties': {
                    'candidates': {'type': 'array', 'items': {'$ref': '#/components/schemas/CandidateBallot'}},
                    'location': {
                        'type': 'object',
                        'properties': {
                            'province': {'type': 'string'},
                            'district': {'type': 'string'},
                            'municipality': {'type': 'string', 'nullable': True},
                            'ward': {'type': 'integer', 'nullable': True},
                        }
                    },
                    'total': {'type': 'integer'},
                    'page': {'type': 'integer'},
                    'page_size': {'type': 'integer'},
                    'total_pages': {'type': 'integer'},
                    'has_next': {'type': 'boolean'},
                    'has_previous': {'type': 'boolean'},
                }
            }
        )
    },
    tags=['Candidates']
)
@api_view(['GET'])
@vary_on_headers('Accept-Language')
@ratelimit(key='ip', rate='30/m', method='GET', block=True)  # 30 requests per minute per IP (ballot generation is expensive)
def my_ballot(request):
    """
    Return candidates for the user's ballot based on their location.

    Implements a relevance scoring system where candidates are sorted by
    how closely they match the user's location.
    """
    # Get location parameters
    province_id = request.GET.get('province_id')
    district_id = request.GET.get('district_id')
    municipality_id = request.GET.get('municipality_id')
    ward_number = request.GET.get('ward_number')

    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)

    # Start with approved candidates only
    # Build Q filters to only include candidates voter can actually vote for
    # Use OR (|) to combine different position levels
    base_filter = Q(status='approved')
    position_filters = Q()  # Empty Q() for combining position-based filters

    # Federal level - House of Representatives (district-based constituencies)
    if district_id:
        position_filters |= Q(
            position_level__in=['house_of_representatives', 'federal'],
            province_id=province_id,
            district_id=district_id
        )

    # Federal level - National Assembly (province-based, elected by electoral college)
    if province_id:
        position_filters |= Q(
            position_level='national_assembly',
            province_id=province_id
        )

    # Provincial level (province-based)
    if province_id:
        position_filters |= Q(
            position_level__in=['provincial_assembly', 'provincial'],
            province_id=province_id
        )

    # Municipal level (municipality-based)
    if municipality_id:
        position_filters |= Q(
            position_level__in=['mayor_chairperson', 'deputy_mayor_vice_chairperson', 'local_executive', 'mayor', 'deputy_mayor', 'local'],
            municipality_id=municipality_id
        )

    # Ward level (ward-based)
    if ward_number and municipality_id:
        position_filters |= Q(
            position_level__in=['ward_chairperson', 'ward_member', 'ward'],
            municipality_id=municipality_id,
            ward_number=ward_number
        )

    # Combine base filter (approved) with position filters (OR of all position types)
    queryset = Candidate.objects.filter(base_filter & position_filters).select_related(
        'province', 'district', 'municipality'
    )

    # Build relevance scoring and location match labels
    relevance_conditions = []
    location_match_conditions = []

    if ward_number and municipality_id:
        relevance_conditions.append(
            When(
                municipality_id=municipality_id,
                ward_number=ward_number,
                position_level='ward',
                then=Value(5)
            )
        )
        location_match_conditions.append(
            When(
                municipality_id=municipality_id,
                ward_number=ward_number,
                position_level='ward',
                then=Value('Exact Ward Match')
            )
        )

    if municipality_id:
        relevance_conditions.append(
            When(
                municipality_id=municipality_id,
                position_level__in=['mayor', 'deputy_mayor', 'local_executive'],
                then=Value(4)
            )
        )
        location_match_conditions.append(
            When(
                municipality_id=municipality_id,
                position_level__in=['mayor', 'deputy_mayor', 'local_executive'],
                then=Value('Municipality Match')
            )
        )

    if district_id:
        relevance_conditions.append(
            When(district_id=district_id, then=Value(3))
        )
        location_match_conditions.append(
            When(district_id=district_id, then=Value('District Match'))
        )

    if province_id:
        relevance_conditions.append(
            When(province_id=province_id, position_level__in=['provincial', 'provincial_assembly'], then=Value(2))
        )
        location_match_conditions.append(
            When(province_id=province_id, position_level__in=['provincial', 'provincial_assembly'], then=Value('Provincial Match'))
        )

    # Federal level candidates
    # Support both old ('federal') and new ('house_of_representatives', 'national_assembly') values
    relevance_conditions.append(
        When(position_level__in=['federal', 'house_of_representatives', 'national_assembly'], then=Value(1))
    )
    location_match_conditions.append(
        When(position_level__in=['federal', 'house_of_representatives', 'national_assembly'], then=Value('Federal Level'))
    )

    # Default relevance
    relevance_conditions.append(When(id__isnull=False, then=Value(0)))
    location_match_conditions.append(When(id__isnull=False, then=Value('Other')))

    # Apply relevance scoring and location match labeling
    queryset = queryset.annotate(
        relevance_score=Case(
            *relevance_conditions,
            default=Value(0),
            output_field=IntegerField()
        ),
        location_match=Case(
            *location_match_conditions,
            default=Value('Other'),
            output_field=CharField()
        )
    ).order_by('-relevance_score', '-created_at')

    # Limit total results to prevent memory issues (max 1000 results)
    # Convert to list to enforce hard limit and avoid queryset issues with Paginator
    total_count = queryset.count()
    if total_count > 1000:
        queryset = list(queryset[:1000])

    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # Serialize
    serializer = CandidateBallotSerializer(page_obj.object_list, many=True, context={'request': request})

    # Build location data
    location_data = {}
    if province_id:
        try:
            from locations.models import Province
            province = Province.objects.get(id=province_id)
            location_data['province'] = province.name_en
        except Province.DoesNotExist:
            pass

    if district_id:
        try:
            from locations.models import District
            district = District.objects.get(id=district_id)
            location_data['district'] = district.name_en
        except District.DoesNotExist:
            pass

    if municipality_id:
        try:
            from locations.models import Municipality
            municipality = Municipality.objects.get(id=municipality_id)
            location_data['municipality'] = municipality.name_en
        except Municipality.DoesNotExist:
            pass

    if ward_number:
        location_data['ward'] = int(ward_number)

    return Response({
        'candidates': serializer.data,
        'location': location_data,
        'total': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    })