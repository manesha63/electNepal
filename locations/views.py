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


@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
@method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True), name='get')
class DistrictsByProvinceView(View):
    def get(self, request):
        pid = request.GET.get('province')
        if not pid:
            return JsonResponse([], safe=False)
        qs = District.objects.filter(province_id=pid).values('id', 'name_en', 'name_ne').order_by('name_en')
        return JsonResponse(list(qs), safe=False)


@method_decorator(cache_page(60 * 10), name='get')  # Cache for 10 minutes
@method_decorator(ratelimit(key='ip', rate='60/m', method='GET', block=True), name='get')
class MunicipalitiesByDistrictView(View):
    def get(self, request):
        did = request.GET.get('district')
        mid = request.GET.get('id')  # For getting specific municipality

        if mid:
            # Get specific municipality by ID
            qs = Municipality.objects.filter(id=mid).values(
                'id', 'name_en', 'name_ne', 'municipality_type', 'total_wards'
            )
            return JsonResponse(list(qs), safe=False)

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
        return JsonResponse({'error': 'Invalid or missing lat/lng'}, status=400)

    # Basic boundary check for Nepal (26.3-30.5°N, 80-88.2°E)
    if not (26.3 <= lat <= 30.5 and 80 <= lng <= 88.2):
        # Track failed request (outside boundaries)
        GeolocationAnalytics.track_request(lat, lng, success=False)
        return JsonResponse({'error': _('Location outside Nepal boundaries')}, status=404)

    # Improved province detection using more accurate boundaries
    # Based on Nepal's actual province geography (approximate but much better)
    province_id = None
    district_name_hint = None

    # Province detection using refined regions
    # Koshi Province (Province 1) - Eastern Nepal
    if lng >= 86.8:
        if lat >= 27.0:
            province_id = 1  # Koshi
            if lat >= 27.8:
                district_name_hint = 'Taplejung'  # Far north-east
            elif 27.4 <= lat < 27.8 and lng >= 87.7:
                district_name_hint = 'Panchthar'
            elif 27.0 <= lat < 27.4 and lng >= 87.5:
                district_name_hint = 'Ilam'
            elif lng >= 87.2:
                district_name_hint = 'Dhankuta'
        elif 26.7 <= lat < 27.0:
            province_id = 1  # Koshi
            district_name_hint = 'Sunsari'
        else:
            province_id = 1  # Koshi
            district_name_hint = 'Morang'

    # Madhesh Province (Province 2) - Southern plains (Terai)
    elif 84.5 <= lng < 86.8 and lat < 27.2:
        province_id = 2  # Madhesh
        if lng >= 86.0:
            district_name_hint = 'Saptari' if lat < 26.6 else 'Siraha'
        elif lng >= 85.3:
            district_name_hint = 'Dhanusha' if lat < 26.8 else 'Mahottari'
        else:
            district_name_hint = 'Bara' if lat < 27.0 else 'Parsa'

    # Bagmati Province (Province 3) - Central Nepal including Kathmandu Valley
    elif 84.5 <= lng < 86.2 and 27.2 <= lat < 28.5:
        province_id = 3  # Bagmati
        # Kathmandu Valley special zone (more precise)
        if 27.6 <= lat <= 27.75 and 85.2 <= lng <= 85.45:
            district_name_hint = 'Kathmandu'
        elif 27.6 <= lat <= 27.73 and 85.35 <= lng <= 85.5:
            district_name_hint = 'Bhaktapur'
        elif 27.58 <= lat <= 27.75 and 85.15 <= lng <= 85.35:
            district_name_hint = 'Lalitpur'
        elif lat >= 28.0:
            district_name_hint = 'Rasuwa'  # Northern mountain district
        elif lat >= 27.8:
            district_name_hint = 'Nuwakot' if lng < 85.3 else 'Sindhupalchok'
        elif lng < 85.0:
            district_name_hint = 'Chitwan'  # Southern Bagmati
        elif lng >= 85.5:
            district_name_hint = 'Kavrepalanchok'

    # Lumbini Province (Province 5) - Western Nepal (Terai to mid-hills)
    # Check Lumbini BEFORE Gandaki to handle overlap correctly
    elif 82.2 <= lng < 84.0 and lat < 27.8:
        province_id = 5  # Lumbini
        if lat >= 27.5:
            # Butwal area (27.7N, 83.46E) and surrounding districts
            district_name_hint = 'Rupandehi' if lng < 83.8 else 'Gulmi'
        elif lat >= 27.0:
            district_name_hint = 'Rupandehi'  # Includes Lumbini, Bhairahawa, Butwal
        else:
            district_name_hint = 'Kapilvastu' if lng < 83.0 else 'Nawalparasi'

    # Gandaki Province (Province 4) - Central-Western Nepal
    elif 83.3 <= lng < 84.8 and 27.5 <= lat < 29.0:
        province_id = 4  # Gandaki
        if lat >= 28.3:
            district_name_hint = 'Manang' if lng < 84.0 else 'Mustang'  # High Himalayas
        elif 27.9 <= lat < 28.3:
            # Pokhara latitude range - more precise
            district_name_hint = 'Kaski' if 28.0 <= lat < 28.3 and 83.8 <= lng < 84.1 else ('Lamjung' if lng < 84.2 else 'Gorkha')
        elif 27.7 <= lat < 27.9:
            district_name_hint = 'Kaski'  # Pokhara area
        else:
            district_name_hint = 'Syangja' if lng < 83.8 else 'Tanahun'

    # Lumbini Province (Province 5) - Northern/hilly areas
    elif 82.2 <= lng < 84.5 and 27.8 <= lat < 28.5:
        province_id = 5  # Lumbini (northern districts)
        district_name_hint = 'Pyuthan' if lng < 83.0 else ('Arghakhanchi' if lng < 83.8 else 'Palpa')

    # Karnali Province (Province 6) - Far-Western Mountains
    elif 81.0 <= lng < 83.3 and lat >= 28.3:
        province_id = 6  # Karnali
        if lat >= 29.5:
            district_name_hint = 'Humla' if lng < 81.8 else 'Mugu'
        elif lat >= 29.0:
            district_name_hint = 'Jumla' if lng < 82.2 else 'Kalikot'
        elif lat >= 28.6:
            district_name_hint = 'Dolpa' if lng >= 82.5 else 'Surkhet'
        else:
            district_name_hint = 'Dailekh' if lng >= 81.7 else 'Jajarkot'

    # Sudurpashchim Province (Province 7) - Far-Western Nepal
    elif lng < 82.5:
        province_id = 7  # Sudurpashchim
        if lat >= 29.5:
            district_name_hint = 'Darchula'  # Far north-west
        elif lat >= 29.0:
            district_name_hint = 'Bajhang' if lng < 81.2 else 'Bajura'
        elif lat >= 28.5:
            # Dhangadhi area and northern districts
            district_name_hint = 'Kailali' if 28.5 <= lat < 28.8 and lng >= 80.5 else ('Achham' if lng < 81.2 else 'Doti')
        elif lat >= 28.0:
            district_name_hint = 'Baitadi' if lng < 80.6 else 'Dadeldhura'
        else:
            district_name_hint = 'Kanchanpur' if lat < 28.6 else 'Kailali'

    # Fallback logic for edge cases
    if province_id is None:
        # Default fallback based on broad regions
        if lng >= 86.8:
            province_id = 1  # Koshi
        elif lng >= 84.5 and lat < 27.2:
            province_id = 2  # Madhesh
        elif lng >= 84.0:
            province_id = 3 if lat >= 27.5 else 2  # Bagmati or Madhesh
        elif lng >= 82.5:
            province_id = 5 if lat < 28.5 else 4  # Lumbini or Gandaki
        elif lat >= 28.3:
            province_id = 6  # Karnali
        else:
            province_id = 7  # Sudurpashchim

    # Try to find district based on hint and province
    district = None
    municipality = None

    if district_name_hint and province_id:
        district = District.objects.filter(
            province_id=province_id,
            name_en__icontains=district_name_hint
        ).first()

        # If district found, try to find the closest municipality (first one as approximation)
        if district:
            municipality = district.municipalities.first()

    # Get province details and build response
    try:
        province = Province.objects.get(id=province_id)
        result = {
            'province': {
                'id': province.id,
                'name_en': province.name_en,
                'name_ne': province.name_ne
            },
            'district': None,
            'municipality': None,
            'ward_number': None
        }

        # Add district if found
        if district:
            result['district'] = {
                'id': district.id,
                'name_en': district.name_en,
                'name_ne': district.name_ne
            }

        # Add municipality if found
        if municipality:
            result['municipality'] = {
                'id': municipality.id,
                'name_en': municipality.name_en,
                'name_ne': municipality.name_ne,
                'code': municipality.code
            }

        # Track successful request
        GeolocationAnalytics.track_request(
            lat, lng, success=True,
            province_name=province.name_en
        )
        return JsonResponse(result)

    except Province.DoesNotExist:
        # Track failed request (could not determine location)
        GeolocationAnalytics.track_request(lat, lng, success=False)
        return JsonResponse({'error': 'Could not determine location'}, status=404)


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
