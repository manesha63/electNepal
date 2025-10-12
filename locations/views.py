from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext as _
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from .models import Province, District, Municipality
from .analytics import GeolocationAnalytics
from core.api_responses import error_response


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


@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
@method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True), name='get')
class DistrictsByProvinceView(View):
    def get(self, request):
        pid_raw = request.GET.get('province')

        # Validate province ID parameter
        try:
            pid = _validate_int_param(pid_raw, 'province')
        except ValueError as e:
            return error_response(str(e), status=400)

        if not pid:
            return JsonResponse([], safe=False)

        qs = District.objects.filter(province_id=pid).values('id', 'name_en', 'name_ne').order_by('name_en')
        return JsonResponse(list(qs), safe=False)


@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
@method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True), name='get')
class MunicipalitiesByDistrictView(View):
    def get(self, request):
        did_raw = request.GET.get('district')
        mid_raw = request.GET.get('id')  # For getting specific municipality

        # Validate municipality ID parameter if provided
        if mid_raw:
            try:
                mid = _validate_int_param(mid_raw, 'municipality id')
            except ValueError as e:
                return error_response(str(e), status=400)

            # Get specific municipality by ID
            qs = Municipality.objects.filter(id=mid).values(
                'id', 'name_en', 'name_ne', 'municipality_type', 'total_wards'
            )
            return JsonResponse(list(qs), safe=False)

        # Validate district ID parameter
        try:
            did = _validate_int_param(did_raw, 'district')
        except ValueError as e:
            return error_response(str(e), status=400)

        if not did:
            return JsonResponse([], safe=False)

        qs = Municipality.objects.filter(district_id=did).values(
            'id', 'name_en', 'name_ne', 'municipality_type', 'total_wards'
        ).order_by('name_en')
        return JsonResponse(list(qs), safe=False)


@require_GET
@ratelimit(key='ip', rate='30/m', method='GET', block=True)  # Stricter limit for georesolve
def geo_resolve(request):
    """
    Resolve latitude/longitude to Province/District/Municipality.
    Uses improved approximation based on Nepal's actual geographical boundaries.
    Note: For production accuracy, consider PostGIS with official boundary shapefiles.
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return error_response('Invalid or missing lat/lng', status=400)

    # ✅ Use shared geolocation logic
    from .geolocation import resolve_coordinates_to_location

    result, status_code = resolve_coordinates_to_location(lat, lng)
    return JsonResponse(result, status=status_code)


@require_GET
def geo_analytics_stats(request):
    """Return geolocation analytics statistics"""
    stats = GeolocationAnalytics.get_stats()
    summary = GeolocationAnalytics.get_summary()

    return JsonResponse({
        'today': stats,
        'summary': summary
    })


@require_GET
@cache_page(60 * 30)  # Cache for 30 minutes (ward data doesn't change often)
@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def municipality_wards_view(request, municipality_id):
    """Return the total number of wards for a specific municipality"""
    municipality = get_object_or_404(Municipality, pk=municipality_id)

    return JsonResponse({
        'municipality_id': municipality.id,
        'municipality_name': municipality.name_en,
        'municipality_name_ne': municipality.name_ne,
        'total_wards': municipality.total_wards
    })
