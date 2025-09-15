from django.contrib import admin
from django.db.models import Count
from .models import Province, District, Municipality


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'district_count', 'municipality_count']
    search_fields = ['name_en', 'name_ne', 'code']
    ordering = ['code']
    
    def district_count(self, obj):
        return obj.districts.count()
    district_count.short_description = 'Districts'
    
    def municipality_count(self, obj):
        return Municipality.objects.filter(district__province=obj).count()
    municipality_count.short_description = 'Municipalities'


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'province', 'municipality_count']
    list_filter = ['province']
    search_fields = ['name_en', 'name_ne', 'code']
    ordering = ['province', 'name_en']
    autocomplete_fields = ['province']
    
    def municipality_count(self, obj):
        return obj.municipalities.count()
    municipality_count.short_description = 'Municipalities'


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_en', 'name_ne', 'municipality_type', 
                    'district', 'province_name', 'total_wards']
    list_filter = ['municipality_type', 'district__province', 'district']
    search_fields = ['name_en', 'name_ne', 'code', 'district__name_en']
    ordering = ['district__province', 'district', 'name_en']
    autocomplete_fields = ['district']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'district', 'municipality_type')
        }),
        ('Names', {
            'fields': ('name_en', 'name_ne')
        }),
        ('Administration', {
            'fields': ('total_wards',)
        }),
    )
    
    def province_name(self, obj):
        return obj.district.province.name_en
    province_name.short_description = 'Province'
    province_name.admin_order_field = 'district__province'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('district', 'district__province')
