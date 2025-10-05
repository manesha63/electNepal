"""
API Views for Locations with proper documentation
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
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
    province_id = request.GET.get('province')

    if province_id:
        try:
            districts = District.objects.filter(province_id=province_id).order_by('name_en')
        except ValueError:
            return Response({'error': 'Invalid province ID'}, status=status.HTTP_400_BAD_REQUEST)
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
    district_id = request.GET.get('district')

    if district_id:
        try:
            municipalities = Municipality.objects.filter(district_id=district_id).order_by('name_en')
        except ValueError:
            return Response({'error': 'Invalid district ID'}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({'error': 'Municipality not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    summary="Resolve GPS coordinates to location",
    description="""
    Converts GPS coordinates (latitude/longitude) to Nepal administrative location.
    Returns the province, district, municipality, and ward information based on coordinates.

    Note: This is a simplified implementation. In production, you would use actual
    geospatial data and libraries like GeoDjango for accurate coordinate-to-location mapping.
    """,
    request=GeoResolveSerializer,
    responses={
        200: GeoResolveResponseSerializer,
        400: OpenApiResponse(description="Invalid coordinates"),
        501: OpenApiResponse(description="Geolocation service not fully implemented")
    },
    tags=['Locations']
)
@api_view(['POST'])
def geo_resolve(request):
    """
    Resolve GPS coordinates to Nepal administrative location.

    This endpoint would typically use geospatial data to map coordinates
    to the correct administrative boundaries.
    """
    serializer = GeoResolveSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    lat = serializer.validated_data['lat']
    lng = serializer.validated_data['lng']

    # Note: This is a placeholder implementation
    # In production, you would use actual geospatial data
    # For now, returning a sample response

    return Response({
        'message': 'Geolocation resolution not fully implemented',
        'note': 'This would require geospatial data and libraries like GeoDjango',
        'coordinates': {'lat': lat, 'lng': lng}
    }, status=status.HTTP_501_NOT_IMPLEMENTED)


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

    # Get total wards
    total_wards = Municipality.objects.aggregate(
        total=Count('total_wards')
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