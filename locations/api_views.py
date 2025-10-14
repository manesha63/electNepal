"""
API Views for Locations with proper documentation
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import Province, District, Municipality
from .serializers import (
    ProvinceSerializer,
    DistrictSerializer,
    MunicipalitySerializer,
    GeoResolveSerializer,
    GeoResolveResponseSerializer,
    LocationStatsSerializer
)
from core.api_responses import error_response, validation_error_response


def _validate_int_param(value, param_name='id'):
    """
    Validate and convert request parameter to integer.
    Prevents SQL injection attempts and invalid input from causing server errors.

    Args:
        value: String value from request.GET
        param_name: Name of parameter for error message

    Returns:
        int or None: Validated integer value, or None if value is empty/None

    Raises:
        ValueError: If value cannot be converted to integer
    """
    if not value:
        return None
    try:
        int_value = int(value)
        # Additional validation: ensure positive integer (IDs are always positive)
        if int_value < 1:
            raise ValueError(f"Invalid {param_name}: must be positive")
        return int_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {param_name} parameter: expected integer, got '{value}'")


@extend_schema(
    summary="Get districts by province",
    description="Returns a list of districts for a given province ID. Used for cascading location dropdowns.",
    parameters=[
        OpenApiParameter(
            name='province',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description='Province ID to filter districts'
        ),
    ],
    responses={
        200: DistrictSerializer(many=True),
        400: OpenApiResponse(description="Invalid province ID")
    },
    tags=['Locations']
)
@api_view(['GET'])
def districts_by_province(request):
    """
    Get all districts, optionally filtered by province.

    Returns districts with their English and Nepali names.
    Used primarily for location selection dropdowns.
    """
    province_id_raw = request.GET.get('province')

    if province_id_raw:
        # Validate province ID parameter BEFORE using it in query
        try:
            province_id = _validate_int_param(province_id_raw, 'province')
        except ValueError as e:
            return error_response(str(e), status=status.HTTP_400_BAD_REQUEST, use_drf=True)

        districts = District.objects.filter(province_id=province_id).order_by('name_en')
    else:
        districts = District.objects.all().order_by('name_en')

    serializer = DistrictSerializer(districts, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get municipalities by district",
    description="Returns a list of municipalities for a given district ID. Used for cascading location dropdowns.",
    parameters=[
        OpenApiParameter(
            name='district',
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description='District ID to filter municipalities'
        ),
    ],
    responses={
        200: MunicipalitySerializer(many=True),
        400: OpenApiResponse(description="Invalid district ID")
    },
    tags=['Locations']
)
@api_view(['GET'])
def municipalities_by_district(request):
    """
    Get all municipalities, optionally filtered by district.

    Returns municipalities with their type (Metropolitan, Sub-Metropolitan, Municipality, Rural Municipality)
    and total number of wards.
    """
    district_id_raw = request.GET.get('district')

    if district_id_raw:
        # Validate district ID parameter BEFORE using it in query
        try:
            district_id = _validate_int_param(district_id_raw, 'district')
        except ValueError as e:
            return error_response(str(e), status=status.HTTP_400_BAD_REQUEST, use_drf=True)

        municipalities = Municipality.objects.filter(district_id=district_id).order_by('name_en')
    else:
        municipalities = Municipality.objects.all().order_by('name_en')

    serializer = MunicipalitySerializer(municipalities, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get ward count for municipality",
    description="Returns the total number of wards in a municipality. Used for ward selection validation.",
    parameters=[
        OpenApiParameter(
            name='municipality_id',
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description='Municipality ID'
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Ward information",
            response={
                'type': 'object',
                'properties': {
                    'municipality_id': {'type': 'integer'},
                    'municipality_name': {'type': 'string'},
                    'total_wards': {'type': 'integer'},
                    'ward_numbers': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'description': 'List of ward numbers (1 to total_wards)'
                    }
                }
            }
        ),
        404: OpenApiResponse(description="Municipality not found")
    },
    tags=['Locations']
)
@api_view(['GET'])
def municipality_wards(request, municipality_id):
    """
    Get ward information for a specific municipality.

    Returns the total number of wards and a list of ward numbers.
    """
    try:
        municipality = Municipality.objects.get(id=municipality_id)
        ward_numbers = list(range(1, municipality.total_wards + 1))

        return Response({
            'municipality_id': municipality.id,
            'municipality_name': municipality.name_en,
            'total_wards': municipality.total_wards,
            'ward_numbers': ward_numbers
        })
    except Municipality.DoesNotExist:
        return error_response('Municipality not found', status=status.HTTP_404_NOT_FOUND, use_drf=True)


@extend_schema(
    summary="Resolve GPS coordinates to location",
    description="""
    Converts GPS coordinates (latitude/longitude) to Nepal administrative location.
    Returns the province, district, municipality, and ward information based on coordinates.

    Uses improved approximation based on Nepal's actual geographical boundaries.
    Note: For production accuracy, consider PostGIS with official boundary shapefiles.

    This is a public endpoint that does not require authentication.
    Supports both GET (with query parameters) and POST (with JSON body) requests.
    """,
    parameters=[
        OpenApiParameter(
            name='lat',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Latitude (for GET requests)',
            required=False
        ),
        OpenApiParameter(
            name='lng',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Longitude (for GET requests)',
            required=False
        ),
    ],
    request=GeoResolveSerializer,
    responses={
        200: GeoResolveResponseSerializer,
        400: OpenApiResponse(description="Invalid coordinates"),
        404: OpenApiResponse(description="Location outside Nepal boundaries")
    },
    tags=['Locations']
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def geo_resolve(request):
    """
    Resolve GPS coordinates to Nepal administrative location.

    Uses geolocation logic to map coordinates to province, district, and municipality
    based on Nepal's geographical boundaries.

    Supports both GET (query parameters) and POST (JSON body) methods.
    """
    # Handle GET requests (query parameters)
    if request.method == 'GET':
        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))
        except (TypeError, ValueError):
            return error_response('Invalid or missing lat/lng parameters', status=status.HTTP_400_BAD_REQUEST, use_drf=True)
    # Handle POST requests (JSON body)
    else:
        serializer = GeoResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error_response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, use_drf=True)
        lat = serializer.validated_data['lat']
        lng = serializer.validated_data['lng']

    # ✅ FIX: Use the actual geolocation logic
    # Import the geolocation resolution function
    from .geolocation import resolve_coordinates_to_location

    # Resolve coordinates to location
    result, status_code = resolve_coordinates_to_location(lat, lng)

    return Response(result, status=status_code)


@extend_schema(
    summary="Get location statistics",
    description="Returns statistical information about Nepal's administrative divisions in the database.",
    responses={
        200: LocationStatsSerializer
    },
    tags=['Locations']
)
@api_view(['GET'])
def location_statistics(request):
    """
    Get statistical information about locations in the database.

    Returns counts of provinces, districts, municipalities, and wards,
    along with breakdown by municipality type.
    """
    # Get counts
    provinces_count = Province.objects.count()
    districts_count = District.objects.count()
    municipalities_count = Municipality.objects.count()

    # Get total wards (sum of all wards across municipalities)
    total_wards = Municipality.objects.aggregate(
        total=Sum('total_wards')
    )['total'] or 0

    # Get municipalities by type
    municipalities_by_type = {}
    for mtype, label in Municipality.MUNICIPALITY_TYPES:
        count = Municipality.objects.filter(municipality_type=mtype).count()
        if count > 0:
            # Convert lazy translation to string
            municipalities_by_type[str(label)] = count

    return Response({
        'total_provinces': provinces_count,
        'total_districts': districts_count,
        'total_municipalities': municipalities_count,
        'total_wards': total_wards,
        'municipalities_by_type': municipalities_by_type,
        'last_updated': timezone.now()
    })


@extend_schema(
    summary="API Health Check",
    description="""
    Health check endpoint that returns API status, version information, and basic system health.

    Use this endpoint to:
    - Verify the API is up and running
    - Check the API version
    - Monitor database connectivity
    - Get server timestamp

    This is a public endpoint that does not require authentication.
    """,
    responses={
        200: OpenApiResponse(
            description="API is healthy",
            response={
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'healthy'},
                    'version': {'type': 'string', 'example': '1.0.0'},
                    'timestamp': {'type': 'string', 'format': 'date-time'},
                    'database': {'type': 'string', 'example': 'connected'},
                    'api_endpoints': {
                        'type': 'object',
                        'properties': {
                            'locations': {'type': 'integer'},
                            'candidates': {'type': 'integer'}
                        }
                    }
                }
            }
        ),
        503: OpenApiResponse(description="Service unavailable")
    },
    tags=['System']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring API availability and status.

    Returns:
    - status: 'healthy' if all systems operational
    - version: API version string
    - timestamp: Current server time
    - database: Database connection status
    - api_endpoints: Count of available API endpoints
    """
    try:
        # Check database connectivity
        db_status = 'connected'
        try:
            # Simple query to verify database is accessible
            Province.objects.count()
        except Exception as e:
            db_status = f'error: {str(e)}'

        # Get API version from Django settings
        from django.conf import settings
        api_version = getattr(settings, 'API_VERSION', '1.0.0')

        # Count available location data
        locations_count = (
            Province.objects.count() +
            District.objects.count() +
            Municipality.objects.count()
        )

        # Count candidates (if database is connected)
        try:
            from candidates.models import Candidate
            candidates_count = Candidate.objects.filter(status='approved').count()
        except:
            candidates_count = 0

        response_data = {
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'version': api_version,
            'timestamp': timezone.now().isoformat(),
            'database': db_status,
            'api_endpoints': {
                'locations': locations_count,
                'candidates': candidates_count
            }
        }

        # Return 503 if database is down, 200 otherwise
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE if db_status != 'connected' else status.HTTP_200_OK

        return Response(response_data, status=status_code)

    except Exception as e:
        # Catch any unexpected errors
        return Response({
            'status': 'error',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat(),
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)