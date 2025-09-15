from django.http import JsonResponse
from django.views import View
from .models import District, Municipality


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
