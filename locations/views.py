from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET
from .models import Province, District, Municipality


class DistrictsByProvinceView(View):
    def get(self, request):
        pid = request.GET.get('province')
        if not pid:
            return JsonResponse([], safe=False)
        qs = District.objects.filter(province_id=pid).values('id', 'name_en', 'name_ne').order_by('name_en')
        return JsonResponse(list(qs), safe=False)


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
def geo_resolve(request):
    """
    Resolve latitude/longitude to Province/District/Municipality/Ward.
    For now, using a simple approximation based on Nepal's geographical regions.
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing lat/lng'}, status=400)

    # Basic boundary check for Nepal (roughly 26.3-30.5 N, 80-88.2 E)
    if not (26.3 <= lat <= 30.5 and 80 <= lng <= 88.2):
        return JsonResponse({'error': 'Location outside Nepal boundaries'}, status=404)

    # Simple region-based approximation for provinces
    # This is a temporary solution until we have proper polygon boundaries
    province_id = None

    if lat >= 29.5:  # Far-western high mountains
        province_id = 6  # Karnali Province
    elif lat >= 28.5:
        if lng <= 83:
            province_id = 7  # Sudurpashchim Province
        elif lng <= 85.5:
            province_id = 5  # Lumbini Province
        else:
            province_id = 1  # Province No. 1
    elif lat >= 27.5:
        if lng <= 84:
            province_id = 5  # Lumbini Province
        elif lng <= 85.5:
            province_id = 3  # Bagmati Province (includes Kathmandu)
        elif lng <= 86.5:
            province_id = 2  # Madhesh Province
        else:
            province_id = 1  # Province No. 1
    else:  # Southern Terai region
        if lng <= 83.5:
            province_id = 7  # Sudurpashchim Province
        elif lng <= 85:
            province_id = 5  # Lumbini Province
        elif lng <= 86:
            province_id = 2  # Madhesh Province
        else:
            province_id = 1  # Province No. 1

    # Special case for Kathmandu valley area
    if 27.6 <= lat <= 27.8 and 85.2 <= lng <= 85.5:
        province_id = 3  # Bagmati Province
        # Try to identify Kathmandu district
        district = District.objects.filter(
            province_id=3,
            name_en__icontains='Kathmandu'
        ).first()

        if district:
            # Try to find Kathmandu municipality
            municipality = Municipality.objects.filter(
                district=district,
                name_en__icontains='Kathmandu'
            ).first()

            if municipality:
                return JsonResponse({
                    'province': {
                        'id': 3,
                        'name_en': 'Bagmati Province',
                        'name_ne': 'बागमती प्रदेश'
                    },
                    'district': {
                        'id': district.id,
                        'name_en': district.name_en,
                        'name_ne': district.name_ne
                    },
                    'municipality': {
                        'id': municipality.id,
                        'name_en': municipality.name_en,
                        'name_ne': municipality.name_ne,
                        'code': municipality.code
                    },
                    'ward_number': None
                })

    # Get province details
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
        return JsonResponse(result)
    except Province.DoesNotExist:
        return JsonResponse({'error': 'Could not determine location'}, status=404)
